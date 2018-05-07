#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""

File name: Core_Model.py

Simple Energy Model Ver 1

This is the heart of the Simple Energy Model. It reads in the case dictionary
that was created in Preprocess_Input.py, and then executes all of the cases.

Technology:
    Generation: natural gas, wind, solar, nuclear
    Energy storage: one generic (a pre-determined round-trip efficiency)
    Curtailment: Yes (free)
    Unmet demand: No
    
Optimization:
    Linear programming (LP)
    Energy balance constraints for the grid and the energy storage facility.

@author: Fan
Time
    Dec 1, 4-8, 11, 19, 22
    Jan 2-4, 24-27
    
"""

# -----------------------------------------------------------------------------



import cvxpy as cvx
import time
import datetime
import numpy as np

# Core function
#   Linear programming
#   Output postprocessing

# -----------------------------------------------------------------------------

def core_model_loop (case_dic):
    num_cases = case_dic['NUM_CASES']
    result_list = [dict() for x in range(num_cases)]
    for case_index in range(num_cases):
        verbose = case_dic['VERBOSE'][case_index]
        if verbose:
            today = datetime.datetime.now()
            print case_index
            print today
        result_list[case_index] = core_model (
            case_dic,
            case_index
            )                                            
    return result_list

# -----------------------------------------------------------------------------

def core_model (case_dic, case_index):
    verbose = case_dic['VERBOSE'][case_index]
    
    demand_series = time_series['DEMAND_SERIES'][case_index] # Assumed to be normalized to 1 kW mean
    solar_series = time_series['SOLAR_SERIES'][case_index] # Assumed to be normalized per kW capacity
    wind_series = time_series['WIND_SERIES'][case_index] # Assumed to be normalized per kW capacity
    if demand_flag >= 0:
        demand_series.fill(demand_flag)
    
    # Fixed costs are assumed to be per time period (1 hour)
    fix_cost_natgas = case_dic['FIX_COST_NATGAS'][case_index]
    fix_cost_solar = case_dic['FIX_COST_SOLAR'][case_index]
    fix_cost_wind = case_dic['FIX_COST_WIND'][case_index]
    fix_cost_nuclear = case_dic['FIX_COST_NUCLEAR'][case_index]
    fix_cost_storage = case_dic['FIX_COST_STORAGE'][case_index]

    # Variable costs are assumed to be kWh
    var_cost_natgas = case_dic['VAR_COST_NATGAS'][case_index]
    var_cost_solar = case_dic['VAR_COST_SOLAR'][case_index]
    var_cost_wind = case_dic['VAR_COST_WIND'][case_index]
    var_cost_nuclear = case_dic['VAR_COST_NUCLEAR'][case_index]
    var_cost_unmet_demand = case_dic['VAR_COST_UNMET_DEMAND'][case_index]
    var_cost_dispatch_from_storage = case_dic['VAR_COST_DISPATCH_FROM_STORAGE'][case_index]
    var_cost_dispatch_to_storage = case_dic['VAR_COST_DISPATCH_TO_STORAGE'][case_index]
    var_cost_storage = case_dic['VAR_COST_STORAGE'][case_index] # variable cost of using storage capacity
    
    storage_charging_efficiency = case_dic['STORAGE_CHARGING_EFFICIENCY'][case_index]
    
    system_components = case_dic['SYSTEM_COMPONENTS'][case_index]
    
    
    num_time_periods = demand_series.size
    start = time.time()
        
    # -------------------------------------------------------------------------
        
    #%% Construct the Problem
    
    # -----------------------------------------------------------------------------
    ## Define Variables
    
    # Number of generation technologies = Fix_Cost_Power.size
    # Number of time steps/units in a given time duration = num_time_periods
    #       num_time_periods returns an integer value
    
    # Capacity_Power = Installed power capacities for all generation technologies = [kW]
    # dispatch_Power = Power generation at each time step for each generator = [kWh]
    
    # dispatch_Curtailment = Curtailed renewable energy generation at each time step = [kWh]
    #   This is more like a dummy variable
    
    # Capacity_Storage = Deployed size of energy storage = [kWh]
    # energy_storage = State of charge for the energy storage = [kWh]
    # dispatch_Storage_Charge = Charging energy flow for energy storage (grid -> storage) = [kW]
    # dispatch_Storage_dispatch = Discharging energy flow for energy storage (grid <- storage) = [kW]
    
    # UnmetDemand = unmet demand/load = [kWh]
    
    fcn2min = 0
    constraints = []

#---------------------- natural gas ------------------------------------------    
    if 'natural_gas' in system_components:
        capacity_natgas = cvx.Variable(1)
        dispatch_natgas = cvx.Variable(num_time_periods)
        constraints += [
                capacity_natgas >= 0,
                dispatch_natgas >= 0,
                dispatch_natgas <= capacity_natgas
                ]
        if capacity_natgas_in >= 0:
            constraints += [ capacity_natgas == capacity_natgas_in ]
        fcn2min += capacity_natgas * fix_cost_natgas + cvx.sum_entries(dispatch_natgas * var_cost_natgas)/num_time_periods
    else:
        capacity_natgas = 0
        dispatch_natgas = np.zeros(num_time_periods)
        
#---------------------- solar ------------------------------------------    
    if 'solar' in system_components:
        capacity_solar = cvx.Variable(1)
        dispatch_solar = cvx.Variable(num_time_periods)
        constraints += [
                capacity_solar >= 0,
                dispatch_solar >= 0, 
                dispatch_solar <= capacity_solar * solar_series 
                ]
        if capacity_solar_in >= 0:
            constraints += [ capacity_solar == capacity_solar_in ]
        fcn2min += capacity_solar * fix_cost_solar + cvx.sum_entries(dispatch_solar * var_cost_solar)/num_time_periods
    else:
        capacity_solar = 0
        dispatch_solar = np.zeros(num_time_periods)
        
#---------------------- wind ------------------------------------------    
    if 'wind' in system_components:
        capacity_wind = cvx.Variable(1)
        dispatch_wind = cvx.Variable(num_time_periods)
        constraints += [
                capacity_wind >= 0,
                dispatch_wind >= 0, 
                dispatch_wind <= capacity_wind * wind_series 
                ]
        if capacity_wind_in >= 0:
            constraints += [ capacity_wind == capacity_wind_in ]
        fcn2min += capacity_wind * fix_cost_wind + cvx.sum_entries(dispatch_wind * var_cost_wind)/num_time_periods
    else:
        capacity_wind = 0
        dispatch_wind = np.zeros(num_time_periods)
        
#---------------------- nuclear ------------------------------------------    
    if 'nuclear' in system_components:
        capacity_nuclear = cvx.Variable(1)
        dispatch_nuclear = cvx.Variable(num_time_periods)
        constraints += [
                capacity_nuclear >= 0,
                dispatch_nuclear >= 0, 
                dispatch_nuclear <= capacity_nuclear 
                ]
        if capacity_nuclear_in >= 0:
            constraints += [ capacity_nuclear == capacity_nuclear_in ]
        fcn2min += capacity_nuclear * fix_cost_nuclear + cvx.sum_entries(dispatch_nuclear * var_cost_nuclear)/num_time_periods
    else:
        capacity_nuclear = 0
        dispatch_nuclear = np.zeros(num_time_periods)
        
#---------------------- storage ------------------------------------------    
    if 'storage' in system_components:
        capacity_storage = cvx.Variable(1)
        dispatch_to_storage = cvx.Variable(num_time_periods)
        dispatch_from_storage = cvx.Variable(num_time_periods)
        energy_storage = cvx.Variable(num_time_periods)
        constraints += [
                capacity_storage >= 0,
                dispatch_to_storage >= 0, 
                dispatch_from_storage >= 0, # dispatch_to_storage is negative value
                energy_storage >= 0,
                energy_storage <= capacity_storage
                ]
        if capacity_storage_in >= 0:
            constraints += [ capacity_storage == capacity_storage_in ]
#        fcn2min += capacity_storage * fix_cost_storage +  \
#            cvx.sum_entries(energy_storage * var_cost_storage)/num_time_periods + \
#            cvx.sum_entries(((dispatch_from_storage**2)**0.5)* var_cost_dispatch_from_storage**0.5)/num_time_periods
        fcn2min += capacity_storage * fix_cost_storage +  \
            cvx.sum_entries(energy_storage * var_cost_storage)/num_time_periods  + \
            cvx.sum_entries(dispatch_to_storage * var_cost_dispatch_to_storage)/num_time_periods + \
            cvx.sum_entries(dispatch_from_storage * var_cost_dispatch_from_storage)/num_time_periods 
 
        for i in xrange(num_time_periods):
#            constraints += [
#                    energy_storage[(i+1) % num_time_periods] == energy_storage[i] - storage_charging_efficiency * dispatch_from_storage[i]
#                    ]
            constraints += [
                    energy_storage[(i+1) % num_time_periods] == energy_storage[i] + storage_charging_efficiency * dispatch_to_storage[i] - dispatch_from_storage[i]
                    ]
#        constraints += [energy_storage[0]==0.0]
    else:
        capacity_storage = 0
        dispatch_to_storage = np.zeros(num_time_periods)
        dispatch_from_storage = np.zeros(num_time_periods)
        energy_storage = np.zeros(num_time_periods)
       
#---------------------- unmet demand ------------------------------------------    
    if 'unmet_demand' in system_components:
        dispatch_unmet_demand = cvx.Variable(num_time_periods)
        constraints += [
                dispatch_unmet_demand >= 0
                ]
        fcn2min += cvx.sum_entries(dispatch_unmet_demand * var_cost_unmet_demand)/num_time_periods
    else:
        dispatch_unmet_demand = np.zeros(num_time_periods)
        
  
#---------------------- natural gas ------------------------------------------    
    constraints += [
            dispatch_natgas + dispatch_solar + dispatch_wind + dispatch_nuclear + dispatch_from_storage +  dispatch_unmet_demand  == 
                demand_series + dispatch_to_storage
            ]    
    
    # -----------------------------------------------------------------------------
    obj = cvx.Minimize(fcn2min)
    
    # -----------------------------------------------------------------------------
    
    # Problem solving
    
    # print cvx.installed_solvers()
    # print >>orig_stdout, cvx.installed_solvers()
    
    # Form and Solve the Problem
    prob = cvx.Problem(obj, constraints)
#    prob.solve(solver = 'GUROBI')
    prob.solve(solver = 'GUROBI',BarConvTol = 1e-11, feasibilityTol = 1e-6)
#    prob.solve(solver = 'GUROBI',BarConvTol = 1e-11, feasibilityTol = 1e-9)
#    prob.solve(solver = 'GUROBI',BarConvTol = 1e-10, feasibilityTol = 1e-8)
#    prob.solve(solver = 'GUROBI',BarConvTol = 1e-8, FeasibilityTol = 1e-6)
    
    end = time.time()
    if verbose:
        print 'system cost ',prob.value
        
    #--------------- curtailment
    dispatch_curtailment = np.zeros(num_time_periods)
    if 'wind' in system_components :
        dispatch_curtailment = dispatch_curtailment + capacity_wind.value.flatten() * wind_series - dispatch_wind.value.flatten()
    if 'solar' in system_components:
        dispatch_curtailment = dispatch_curtailment + capacity_solar.value.flatten() * solar_series - dispatch_solar.value.flatten()
    if 'nuclear' in system_components:
        dispatch_curtailment = dispatch_curtailment + capacity_nuclear.value.flatten()  - dispatch_nuclear.value.flatten()
 
        
        
    dispatch_curtailment = np.array(dispatch_curtailment.flatten())
    # -----------------------------------------------------------------------------
    
    result={
            'system_cost':prob.value,
            'problem_status':prob.status,
            'dispatch_curtailment':dispatch_curtailment
            }
    
    if 'natural_gas' in system_components:
        result['capacity_natgas'] = np.asscalar(capacity_natgas.value)
        result['dispatch_natgas'] = np.array(dispatch_natgas.value).flatten()
    else:
        result['capacity_natgas'] = capacity_natgas
        result['dispatch_natgas'] = dispatch_natgas

    if 'solar' in system_components:
        result['capacity_solar'] = np.asscalar(capacity_solar.value)
        result['dispatch_solar'] = np.array(dispatch_solar.value).flatten()
    else:
        result['capacity_solar'] = capacity_solar
        result['dispatch_solar'] = dispatch_solar

    if 'wind' in system_components:
        result['capacity_wind'] = np.asscalar(capacity_wind.value)
        result['dispatch_wind'] = np.array(dispatch_wind.value).flatten()
    else:
        result['capacity_wind'] = capacity_wind
        result['dispatch_wind'] = dispatch_wind

    if 'nuclear' in system_components:
        result['capacity_nuclear'] = np.asscalar(capacity_nuclear.value)
        result['dispatch_nuclear'] = np.array(dispatch_nuclear.value).flatten()
    else:
        result['capacity_nuclear'] = capacity_nuclear
        result['dispatch_nuclear'] = dispatch_nuclear

    if 'storage' in system_components:
        result['capacity_storage'] = np.asscalar(capacity_storage.value)
        result['dispatch_to_storage'] = np.array(dispatch_to_storage.value).flatten()
        result['dispatch_from_storage'] = np.array(dispatch_from_storage.value).flatten()
        result['energy_storage'] = np.array(energy_storage.value).flatten()
    else:
        result['capacity_storage'] = capacity_storage
        result['dispatch_to_storage'] = dispatch_to_storage
        result['dispatch_from_storage'] = dispatch_from_storage
        result['energy_storage'] = energy_storage
        
    if 'unmet_demand' in system_components:
        result['dispatch_unmet_demand'] = np.array(dispatch_unmet_demand.value).flatten()
    else:
        result['dispatch_unmet_demand'] = dispatch_unmet_demand
        

    return result
  