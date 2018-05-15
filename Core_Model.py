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

def core_model_loop (global_dic, case_dic_list):
    verbose = global_dic['VERBOSE']
    if verbose:
        print "Core_Model.py: Entering core model loop"
    num_cases = len(case_dic_list)
    
    result_list = [dict() for x in range(num_cases)]
    for case_index in range(num_cases):

        if verbose:
            today = datetime.datetime.now()
            print 'solving ',case_dic_list[case_index]['CASE_NAME']
            print today
        result_list[case_index] = core_model (global_dic, case_dic_list[case_index])                                            
    return result_list

# -----------------------------------------------------------------------------

def core_model (global_dic, case_dic):
    verbose = global_dic['VERBOSE']
    if verbose:
        print "Core_Model.py: processing case ",case_dic['CASE_NAME']
    demand_series = case_dic['DEMAND_SERIES'] # Assumed to be normalized to 1 kW mean
    solar_series = case_dic['SOLAR_SERIES'] # Assumed to be normalized per kW capacity
    wind_series = case_dic['WIND_SERIES'] # Assumed to be normalized per kW capacity

    
    # Fixed costs are assumed to be per time period (1 hour)
    capacity_cost_natgas = case_dic['CAPACITY_COST_NATGAS']
    capacity_cost_solar = case_dic['CAPACITY_COST_SOLAR']
    capacity_cost_wind = case_dic['CAPACITY_COST_WIND']
    capacity_cost_nuclear = case_dic['CAPACITY_COST_NUCLEAR']
    capacity_cost_storage = case_dic['CAPACITY_COST_STORAGE']

    # Variable costs are assumed to be kWh
    dispatch_cost_natgas = case_dic['DISPATCH_COST_NATGAS']
    dispatch_cost_solar = case_dic['DISPATCH_COST_SOLAR']
    dispatch_cost_wind = case_dic['DISPATCH_COST_WIND']
    dispatch_cost_nuclear = case_dic['DISPATCH_COST_NUCLEAR']
    dispatch_cost_unmet_demand = case_dic['DISPATCH_COST_UNMET_DEMAND']
    dispatch_cost_dispatch_from_storage = case_dic['DISPATCH_COST_DISPATCH_FROM_STORAGE']
    dispatch_cost_dispatch_to_storage = case_dic['DISPATCH_COST_DISPATCH_TO_STORAGE']
    dispatch_cost_storage = case_dic['DISPATCH_COST_STORAGE'] # variable cost of using storage capacity
    
    storage_charging_efficiency = case_dic['STORAGE_CHARGING_EFFICIENCY']
    
    system_components = case_dic['SYSTEM_COMPONENTS']
      
    num_time_periods = len(demand_series)

    # -------------------------------------------------------------------------
        
    #%% Construct the Problem
    
    # -----------------------------------------------------------------------------
    ## Define Variables
    
    # Number of generation technologies = capacity_cost_Power.size
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
    if 'NATGAS' in system_components:
        capacity_natgas = cvx.Variable(1)
        dispatch_natgas = cvx.Variable(num_time_periods)
        constraints += [
                capacity_natgas >= 0,
                dispatch_natgas >= 0,
                dispatch_natgas <= capacity_natgas
                ]
        fcn2min += capacity_natgas * capacity_cost_natgas + cvx.sum_entries(dispatch_natgas * dispatch_cost_natgas)/num_time_periods
    else:
        capacity_natgas = 0
        dispatch_natgas = np.zeros(num_time_periods)
        
#---------------------- solar ------------------------------------------    
    if 'SOLAR' in system_components:
        capacity_solar = cvx.Variable(1)
        dispatch_solar = cvx.Variable(num_time_periods)
        constraints += [
                capacity_solar >= 0,
                dispatch_solar >= 0, 
                dispatch_solar <= capacity_solar * solar_series 
                ]
        fcn2min += capacity_solar * capacity_cost_solar + cvx.sum_entries(dispatch_solar * dispatch_cost_solar)/num_time_periods
    else:
        capacity_solar = 0
        dispatch_solar = np.zeros(num_time_periods)
        
#---------------------- wind ------------------------------------------    
    if 'WIND' in system_components:
        capacity_wind = cvx.Variable(1)
        dispatch_wind = cvx.Variable(num_time_periods)
        constraints += [
                capacity_wind >= 0,
                dispatch_wind >= 0, 
                dispatch_wind <= capacity_wind * wind_series 
                ]
        fcn2min += capacity_wind * capacity_cost_wind + cvx.sum_entries(dispatch_wind * dispatch_cost_wind)/num_time_periods
    else:
        capacity_wind = 0
        dispatch_wind = np.zeros(num_time_periods)
        
#---------------------- nuclear ------------------------------------------    
    if 'NUCLEAR' in system_components:
        capacity_nuclear = cvx.Variable(1)
        dispatch_nuclear = cvx.Variable(num_time_periods)
        constraints += [
                capacity_nuclear >= 0,
                dispatch_nuclear >= 0, 
                dispatch_nuclear <= capacity_nuclear 
                ]
        fcn2min += capacity_nuclear * capacity_cost_nuclear + cvx.sum_entries(dispatch_nuclear * dispatch_cost_nuclear)/num_time_periods
    else:
        capacity_nuclear = 0
        dispatch_nuclear = np.zeros(num_time_periods)
        
#---------------------- storage ------------------------------------------    
    if 'STORAGE' in system_components:
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
#        fcn2min += capacity_storage * capacity_cost_storage +  \
#            cvx.sum_entries(energy_storage * dispatch_cost_storage)/num_time_periods + \
#            cvx.sum_entries(((dispatch_from_storage**2)**0.5)* dispatch_cost_dispatch_from_storage**0.5)/num_time_periods
        fcn2min += capacity_storage * capacity_cost_storage +  \
            cvx.sum_entries(energy_storage * dispatch_cost_storage)/num_time_periods  + \
            cvx.sum_entries(dispatch_to_storage * dispatch_cost_dispatch_to_storage)/num_time_periods + \
            cvx.sum_entries(dispatch_from_storage * dispatch_cost_dispatch_from_storage)/num_time_periods 
 
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
    if 'UNMET_DEMAND' in system_components:
        dispatch_unmet_demand = cvx.Variable(num_time_periods)
        constraints += [
                dispatch_unmet_demand >= 0
                ]
        fcn2min += cvx.sum_entries(dispatch_unmet_demand * dispatch_cost_unmet_demand)/num_time_periods
    else:
        dispatch_unmet_demand = np.zeros(num_time_periods)
        
  
#---------------------- dispatch constraint ------------------------------------------    
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
            'SYSTEM_COST':prob.value,
            'PROBLEM_STATUS':prob.status,
            'DISPATCH_CURTAILMENT':dispatch_curtailment
            }
    
    if 'NATGAS' in system_components:
        result['CAPACITY_NATGAS'] = np.asscalar(capacity_natgas.value)
        result['DISPATCH_NATGAS'] = np.array(dispatch_natgas.value).flatten()
    else:
        result['CAPACITY_NATGAS'] = capacity_natgas
        result['DISPATCH_NATGAS'] = dispatch_natgas

    if 'SOLAR' in system_components:
        result['CAPACITY_SOLAR'] = np.asscalar(capacity_solar.value)
        result['DISPATCH_SOLAR'] = np.array(dispatch_solar.value).flatten()
    else:
        result['CAPACITY_SOLAR'] = capacity_solar
        result['DISPATCH_SOLAR'] = dispatch_solar

    if 'WIND' in system_components:
        result['CAPACITY_WIND'] = np.asscalar(capacity_wind.value)
        result['DISPATCH_WIND'] = np.array(dispatch_wind.value).flatten()
    else:
        result['CAPACITY_WIND'] = capacity_wind
        result['DISPATCH_WIND'] = dispatch_wind

    if 'NUCLEAR' in system_components:
        result['CAPACITY_NUCLEAR'] = np.asscalar(capacity_nuclear.value)
        result['DISPATCH_NUCLEAR'] = np.array(dispatch_nuclear.value).flatten()
    else:
        result['CAPACITY_NUCLEAR'] = capacity_nuclear
        result['DISPATCH_NUCLEAR'] = dispatch_nuclear

    if 'STORAGE' in system_components:
        result['CAPACITY_STORAGE'] = np.asscalar(capacity_storage.value)
        result['DISPATCH_TO_STORAGE'] = np.array(dispatch_to_storage.value).flatten()
        result['DISPATCH_FROM_STORAGE'] = np.array(dispatch_from_storage.value).flatten()
        result['ENERGY_STORAGE'] = np.array(energy_storage.value).flatten()
    else:
        result['CAPACITY_STORAGE'] = capacity_storage
        result['DISPATCH_TO_STORAGE'] = dispatch_to_storage
        result['DISPATCH_FROM_STORAGE'] = dispatch_from_storage
        result['ENERGY_STORAGE'] = energy_storage
        
    if 'UNMET_DEMAND' in system_components:
        result['DISPATCH_UNMET_DEMAND'] = np.array(dispatch_unmet_demand.value).flatten()
    else:
        result['DISPATCH_UNMET_DEMAND'] = dispatch_unmet_demand
        

    return result
  