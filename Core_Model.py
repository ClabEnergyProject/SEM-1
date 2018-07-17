#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Simple Energy Model Ver 1

File name: Core_Model.py
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
    
Current version: my180628-const-nuc-A
    Modified from SEM-1-my180627 for nuclear vs. renewables analysis.
    Nuclear, wind, and solar represented by Formulation A (previously Formulation 2A') with nonzero curtailment (generic equations).
    Note: This version is the same as SEM-1-my180628 but renamed to avoid confusion.

Updates (from SEM-1-my180628):
    (a) separated curtailment of solar, wind, and nuclear
        - checked results against -my180627, system cost and total curtailment in agreement
    
Planned updates:
    (a) write script for constant nuclear with curtailment as decision variables (Formulation 2B)
    Note: see emails and notes for two formulations

"""

#%% import modules

import cvxpy as cvx
import time
import datetime
import numpy as np

#%% loop to step through assumption list

def core_model_loop (global_dic, case_dic_list):
    
    verbose = global_dic['VERBOSE']
    if verbose:
        print "Core_Model.py: Entering core model loop"
    num_cases = len(case_dic_list)
    
    result_list = [dict() for x in range(num_cases)]
    for case_index in range(num_cases):

        if verbose:
            today = datetime.datetime.now()
            print 'solving ',case_dic_list[case_index]['CASE_NAME'],' time = ',today
        result_list[case_index] = core_model (global_dic, case_dic_list[case_index])                                            
        if verbose:
            today = datetime.datetime.now()
            print 'solved  ',case_dic_list[case_index]['CASE_NAME'],' time = ',today
            
    return result_list

#%% core energy balance and optimization model

def core_model (global_dic, case_dic):
    
    # "verbose" variable (for output on console) and scaling factors
    verbose = global_dic['VERBOSE']
    numerics_cost_scaling = global_dic['NUMERICS_COST_SCALING']
    numerics_demand_scaling = global_dic['NUMERICS_DEMAND_SCALING']
    if verbose:
        print "Core_Model.py: processing case ",case_dic['CASE_NAME']
        
    # demand, solar capacity factors, wind capacity factors
    demand_series = np.array(case_dic['DEMAND_SERIES'])*numerics_demand_scaling 
    solar_series = case_dic['SOLAR_SERIES']     # assumed to be normalized per kW capacity
    wind_series = case_dic['WIND_SERIES']       # assumed to be normalized per kW capacity

    # fixed costs (capacity costs) are assumed to be $ per time period (1 hour)
    capacity_cost_natgas = case_dic['CAPACITY_COST_NATGAS']*numerics_cost_scaling
    capacity_cost_solar = case_dic['CAPACITY_COST_SOLAR']*numerics_cost_scaling
    capacity_cost_wind = case_dic['CAPACITY_COST_WIND']*numerics_cost_scaling
    capacity_cost_nuclear = case_dic['CAPACITY_COST_NUCLEAR']*numerics_cost_scaling
    capacity_cost_storage = case_dic['CAPACITY_COST_STORAGE']*numerics_cost_scaling
    capacity_cost_pgp_storage = case_dic['CAPACITY_COST_PGP_STORAGE']*numerics_cost_scaling
    capacity_cost_pgp_fuel_cell = case_dic['CAPACITY_COST_PGP_FUEL_CELL']*numerics_cost_scaling

    # variable costs (dispatch costs) are assumed to be $ per kWh
    dispatch_cost_natgas = case_dic['DISPATCH_COST_NATGAS']*numerics_cost_scaling
    dispatch_cost_solar = case_dic['DISPATCH_COST_SOLAR']*numerics_cost_scaling
    dispatch_cost_wind = case_dic['DISPATCH_COST_WIND']*numerics_cost_scaling
    dispatch_cost_nuclear = case_dic['DISPATCH_COST_NUCLEAR']*numerics_cost_scaling
    dispatch_cost_unmet_demand = case_dic['DISPATCH_COST_UNMET_DEMAND']*numerics_cost_scaling
    dispatch_cost_from_storage = case_dic['DISPATCH_COST_FROM_STORAGE']*numerics_cost_scaling
    dispatch_cost_to_storage = case_dic['DISPATCH_COST_TO_STORAGE']*numerics_cost_scaling
    dispatch_cost_from_pgp_storage = case_dic['DISPATCH_COST_FROM_PGP_STORAGE']*numerics_cost_scaling
    dispatch_cost_to_pgp_storage = case_dic['DISPATCH_COST_TO_PGP_STORAGE']*numerics_cost_scaling

    # storage efficiencies
    storage_charging_efficiency = case_dic['STORAGE_CHARGING_EFFICIENCY']
    storage_charging_time       = case_dic['STORAGE_CHARGING_TIME']
    storage_decay_rate          = case_dic['STORAGE_DECAY_RATE']    # fraction of stored electricity lost each hour
    pgp_storage_charging_efficiency = case_dic['PGP_STORAGE_CHARGING_EFFICIENCY']
    
    # system components (technologies)
    system_components = case_dic['SYSTEM_COMPONENTS']
    
    # number of hours simulated
    num_time_periods = len(demand_series)

    # -------------------------------------------------------------------------
    # construct optimization problem

    start_time = time.time()    # timer starts

    # initialize objective function and constraints
    fcn2min = 0
    constraints = []
    
    # set decision variables and constraints for each technology
    
    # generation technology
        # capacity_[generation] = installed capacity for each generation technology [kW]
        # dispatch_[generation] = energy generated to meet demand at all timesteps (timestep size = 1hr) from each generator [kWh]
        # curtailment_[generation] = energy generated but unused ("curtailed") at all timesteps, specifically from solar, wind, and nuclear
    
    # storage
        # capacity_storage = deployed (installed) size of energy storage [kWh]
        # energy_storage = state of charge at all timesteps [kWh]
        # dispatch_to_storage = charging energy flow for energy storage (grid -> storage) at all timesteps [kWh]
        # dispatch_from_storage = discharging energy flow for energy storage (grid <- storage) at all timesteps [kWh]
    
    # unmet demand
        # dispatch_unmet_demand = unmet demand at all timesteps as determined from energy balance [kWh]

    #---------------------- natural gas --------------------------------------- 
    if 'NATGAS' in system_components:
        
        # decision variables
        capacity_natgas = cvx.Variable(1)
        dispatch_natgas = cvx.Variable(num_time_periods)
        
        # constraints
        constraints += [
                capacity_natgas >= 0,
                dispatch_natgas >= 0,
                dispatch_natgas <= capacity_natgas
                ]
        
        # update objective function (+ contribution to system cost)
        fcn2min += capacity_natgas * capacity_cost_natgas + cvx.sum_entries(dispatch_natgas * dispatch_cost_natgas)/num_time_periods
        
    else:   # if natural gas not in system, set capacity and dispatch to zero
        capacity_natgas = 0
        dispatch_natgas = np.zeros(num_time_periods)
        
    #---------------------- solar ---------------------------------------------
    if 'SOLAR' in system_components:
        
        # decision variables
        capacity_solar = cvx.Variable(1)
        dispatch_solar = cvx.Variable(num_time_periods)
        
        # constraints        
        constraints += [
                capacity_solar >= 0,
                dispatch_solar >= 0, 
                dispatch_solar <= capacity_solar * solar_series 
                ]
        
        # update objective function (+ contribution to system cost)
        fcn2min += capacity_solar * capacity_cost_solar + cvx.sum_entries(dispatch_solar * dispatch_cost_solar)/num_time_periods

    else:   # if solar not in system, set capacity and dispatch to zero
        capacity_solar = 0
        dispatch_solar = np.zeros(num_time_periods)
        
    #---------------------- wind ----------------------------------------------
    if 'WIND' in system_components:
        
        # decision variables
        capacity_wind = cvx.Variable(1)
        dispatch_wind = cvx.Variable(num_time_periods)
        
        # constraints
        constraints += [
                capacity_wind >= 0,
                dispatch_wind >= 0, 
                dispatch_wind <= capacity_wind * wind_series 
                ]
                
        # update objective function (+ contribution to system cost)
        fcn2min += capacity_wind * capacity_cost_wind + cvx.sum_entries(dispatch_wind * dispatch_cost_wind)/num_time_periods
    
    else:   # if wind not in system, set capacity and dispatch to zero
        capacity_wind = 0
        dispatch_wind = np.zeros(num_time_periods)
        
    #---------------------- nuclear -------------------------------------------
    if 'NUCLEAR' in system_components:
        
        # decision variables
        capacity_nuclear = cvx.Variable(1)
        dispatch_nuclear = cvx.Variable(num_time_periods)
        
        # constraints
        constraints += [
                capacity_nuclear >= 0,
                dispatch_nuclear >= 0, 
                dispatch_nuclear <= capacity_nuclear 
                ]
                
        # update objective function (+ contribution to system cost)
        fcn2min += capacity_nuclear * capacity_cost_nuclear + cvx.sum_entries(dispatch_nuclear * dispatch_cost_nuclear)/num_time_periods
    
    else:   # if nuclear not in system, set capacity and dispatch to zero
        capacity_nuclear = 0
        dispatch_nuclear = np.zeros(num_time_periods)
        
    #---------------------- storage -------------------------------------------
    if 'STORAGE' in system_components:
        
        # decision variables
        capacity_storage = cvx.Variable(1)
        dispatch_to_storage = cvx.Variable(num_time_periods)
        dispatch_from_storage = cvx.Variable(num_time_periods)
        energy_storage = cvx.Variable(num_time_periods)
        
        # constraints
        constraints += [
                capacity_storage >= 0,
                dispatch_to_storage >= 0, 
                dispatch_to_storage <= capacity_storage / storage_charging_time,
                dispatch_from_storage >= 0,
                dispatch_from_storage <= capacity_storage / storage_charging_time,
                dispatch_from_storage <= energy_storage * (1 - storage_decay_rate),     # one cannot dispatch more from storage in a time step than is in the battery (redundant?)
                energy_storage >= 0,
                energy_storage <= capacity_storage
                ]
        # charge balance between consecutive timesteps and between simulation cycles (between last timestep in current cycle and first timestep in next cycle)
            # essentially: total disptach from storage = total dispatch to storage within one simulation cycle
        for i in xrange(num_time_periods):
            constraints += [
                    energy_storage[(i+1) % num_time_periods] == energy_storage[i] + storage_charging_efficiency * dispatch_to_storage[i] - dispatch_from_storage[i] - energy_storage[i]*storage_decay_rate
                    ]
       
        # update objective function (+ contribution to system cost)
        fcn2min += capacity_storage * capacity_cost_storage +  \
            cvx.sum_entries(dispatch_to_storage * dispatch_cost_to_storage)/num_time_periods + \
            cvx.sum_entries(dispatch_from_storage * dispatch_cost_from_storage)/num_time_periods 

    else:   # if storage not in system, set capacity and dispatch to zero  
        capacity_storage = 0
        dispatch_to_storage = np.zeros(num_time_periods)
        dispatch_from_storage = np.zeros(num_time_periods)
        energy_storage = np.zeros(num_time_periods)
       
    #------------------- pgp storage (power to gas to power) ------------------
    if 'PGP_STORAGE' in system_components:
        
        # decision variables
        capacity_pgp_storage = cvx.Variable(1)      # energy storage capacity in kWh (i.e., tank size)
        capacity_pgp_fuel_cell = cvx.Variable(1)    # maximum power input / output (in kW) fuel cell / electrolyzer size
        dispatch_to_pgp_storage = cvx.Variable(num_time_periods)
        dispatch_from_pgp_storage = cvx.Variable(num_time_periods)
        energy_pgp_storage = cvx.Variable(num_time_periods)     # amount of energy currently stored in tank
        
        # constraints        
        constraints += [
                capacity_pgp_storage >= 0,
                capacity_pgp_fuel_cell >= 0,
                dispatch_to_pgp_storage >= 0, 
                dispatch_to_pgp_storage <= capacity_pgp_fuel_cell,
                dispatch_from_pgp_storage >= 0,
                dispatch_from_pgp_storage <= capacity_pgp_fuel_cell,
                dispatch_from_pgp_storage <= energy_pgp_storage, # one cannot dispatch more from storage in a time step than is in the battery (redundant?)
                energy_pgp_storage >= 0,
                energy_pgp_storage <= capacity_pgp_storage
                ]
                
        # charge balance between consecutive timesteps and between simulation cycles (between last timestep in current cycle and first timestep in next cycle)
            # essentially: total disptach from storage = total dispatch to storage within one simulation cycle
        for i in xrange(num_time_periods):
            constraints += [
                    energy_pgp_storage[(i+1) % num_time_periods] == energy_pgp_storage[i] + pgp_storage_charging_efficiency * dispatch_to_pgp_storage[i] - dispatch_from_pgp_storage[i] 
                    ]

        # update objective function (+ contribution to system cost)
        fcn2min += capacity_pgp_storage * capacity_cost_pgp_storage +  capacity_pgp_fuel_cell * capacity_cost_pgp_fuel_cell + \
            cvx.sum_entries(dispatch_to_pgp_storage * dispatch_cost_to_pgp_storage)/num_time_periods + \
            cvx.sum_entries(dispatch_from_pgp_storage * dispatch_cost_from_pgp_storage)/num_time_periods 

    else:   # if pgp storage not in system, set capacity and dispatch to zero  
        capacity_pgp_storage = 0
        capacity_pgp_fuel_cell = 0
        dispatch_to_pgp_storage = np.zeros(num_time_periods)
        dispatch_from_pgp_storage = np.zeros(num_time_periods)
        energy_pgp_storage = np.zeros(num_time_periods)

    #---------------------- unmet demand --------------------------------------
    if 'UNMET_DEMAND' in system_components:
        
        # decision variables
        dispatch_unmet_demand = cvx.Variable(num_time_periods)
        
        # constraints
        constraints += [
                dispatch_unmet_demand >= 0
                ]
        
        # update objective function (+ contribution to system cost)
        fcn2min += cvx.sum_entries(dispatch_unmet_demand * dispatch_cost_unmet_demand)/num_time_periods
        
    else:   # if unmet demand not in system, set capacity and dispatch to zero  
        dispatch_unmet_demand = np.zeros(num_time_periods)
        
  
    #---------------------- system energy balance -----------------------------
    constraints += [
            dispatch_natgas + dispatch_solar + dispatch_wind + dispatch_nuclear + dispatch_from_storage + dispatch_from_pgp_storage + dispatch_unmet_demand  == 
                demand_series + dispatch_to_storage + dispatch_to_pgp_storage
            ]    
    
    # -------------------------------------------------------------------------
    # solve optimization problem

    # objective function = minimize hourly system cost
    obj = cvx.Minimize(fcn2min)
    
    # optimization problem to be solved
    prob = cvx.Problem(obj, constraints)
    
    # solve problem (default solver parameters: BarConvTol = 1e-8, FeasibilityTol = 1e-6)
    prob.solve(solver = 'GUROBI')
    
    #--------------------------------------------------------------------------
    # print out objective function value and computation time  
    
    end_time = time.time()  # timer ends

    if verbose:
        print 'system cost: ', prob.value/(numerics_cost_scaling * numerics_demand_scaling), '$/kWh'
        print 'runtime: ', (end_time - start_time), 'seconds'
        
    #--------------- curtailment ----------------------------------------------
    curtailment_wind = np.zeros(num_time_periods)
    curtailment_solar = np.zeros(num_time_periods)
    curtailment_nuclear = np.zeros(num_time_periods)
    if 'WIND' in system_components :
        curtailment_wind = capacity_wind.value.flatten() * wind_series - dispatch_wind.value.flatten()
    if 'SOLAR' in system_components:
        curtailment_solar = capacity_solar.value.flatten() * solar_series - dispatch_solar.value.flatten()
    if 'NUCLEAR' in system_components:
        curtailment_nuclear = capacity_nuclear.value.flatten() - dispatch_nuclear.value.flatten()   
        
    # -------------------------------------------------------------------------
    # results to output (pickle and .csv files)
    
    result={
            'SYSTEM_COST':prob.value/(numerics_cost_scaling * numerics_demand_scaling),
            'PROBLEM_STATUS':prob.status,
            }
    
    if 'NATGAS' in system_components:
        result['CAPACITY_NATGAS'] = np.asscalar(capacity_natgas.value)/numerics_demand_scaling
        result['DISPATCH_NATGAS'] = np.array(dispatch_natgas.value).flatten()/numerics_demand_scaling
    else:
        result['CAPACITY_NATGAS'] = capacity_natgas/numerics_demand_scaling
        result['DISPATCH_NATGAS'] = dispatch_natgas/numerics_demand_scaling

    if 'SOLAR' in system_components:
        result['CAPACITY_SOLAR'] = np.asscalar(capacity_solar.value)/numerics_demand_scaling
        result['DISPATCH_SOLAR'] = np.array(dispatch_solar.value).flatten()/numerics_demand_scaling
        result['CURTAILMENT_SOLAR'] = np.array(curtailment_solar.flatten()) / numerics_demand_scaling
    else:
        result['CAPACITY_SOLAR'] = capacity_solar/numerics_demand_scaling
        result['DISPATCH_SOLAR'] = dispatch_solar/numerics_demand_scaling
        result['CURTAILMENT_SOLAR'] = curtailment_solar / numerics_demand_scaling
        
    if 'WIND' in system_components:
        result['CAPACITY_WIND'] = np.asscalar(capacity_wind.value)/numerics_demand_scaling
        result['DISPATCH_WIND'] = np.array(dispatch_wind.value).flatten()/numerics_demand_scaling
        result['CURTAILMENT_WIND'] = np.array(curtailment_wind.flatten()) / numerics_demand_scaling
    else:
        result['CAPACITY_WIND'] = capacity_wind/numerics_demand_scaling
        result['DISPATCH_WIND'] = dispatch_wind/numerics_demand_scaling
        result['CURTAILMENT_WIND'] = curtailment_wind / numerics_demand_scaling

    if 'NUCLEAR' in system_components:
        result['CAPACITY_NUCLEAR'] = np.asscalar(capacity_nuclear.value)/numerics_demand_scaling
        result['DISPATCH_NUCLEAR'] = np.array(dispatch_nuclear.value).flatten()/numerics_demand_scaling
        result['CURTAILMENT_NUCLEAR'] = np.array(curtailment_nuclear.flatten()) / numerics_demand_scaling
    else:
        result['CAPACITY_NUCLEAR'] = capacity_nuclear/numerics_demand_scaling
        result['DISPATCH_NUCLEAR'] = dispatch_nuclear/numerics_demand_scaling
        result['CURTAILMENT_NUCLEAR'] = curtailment_nuclear / numerics_demand_scaling

    if 'STORAGE' in system_components:
        result['CAPACITY_STORAGE'] = np.asscalar(capacity_storage.value)/numerics_demand_scaling
        result['DISPATCH_TO_STORAGE'] = np.array(dispatch_to_storage.value).flatten()/numerics_demand_scaling
        result['DISPATCH_FROM_STORAGE'] = np.array(dispatch_from_storage.value).flatten()/numerics_demand_scaling
        result['ENERGY_STORAGE'] = np.array(energy_storage.value).flatten()/numerics_demand_scaling
    else:
        result['CAPACITY_STORAGE'] = capacity_storage/numerics_demand_scaling
        result['DISPATCH_TO_STORAGE'] = dispatch_to_storage/numerics_demand_scaling
        result['DISPATCH_FROM_STORAGE'] = dispatch_from_storage/numerics_demand_scaling
        result['ENERGY_STORAGE'] = energy_storage/numerics_demand_scaling
        
    if 'PGP_STORAGE' in system_components:
        result['CAPACITY_PGP_STORAGE'] = np.asscalar(capacity_pgp_storage.value)/numerics_demand_scaling
        result['CAPACITY_PGP_FUEL_CELL'] = np.asscalar(capacity_pgp_fuel_cell.value)/numerics_demand_scaling
        result['DISPATCH_TO_PGP_STORAGE'] = np.array(dispatch_to_pgp_storage.value).flatten()/numerics_demand_scaling
        result['DISPATCH_FROM_PGP_STORAGE'] = np.array(dispatch_from_pgp_storage.value).flatten()/numerics_demand_scaling
        result['ENERGY_PGP_STORAGE'] = np.array(energy_pgp_storage.value).flatten()/numerics_demand_scaling
    else:
        result['CAPACITY_PGP_STORAGE'] = capacity_pgp_storage/numerics_demand_scaling
        result['CAPACITY_PGP_FUEL_CELL'] = capacity_pgp_fuel_cell/numerics_demand_scaling
        result['DISPATCH_TO_PGP_STORAGE'] = dispatch_to_pgp_storage/numerics_demand_scaling
        result['DISPATCH_FROM_PGP_STORAGE'] = dispatch_from_pgp_storage/numerics_demand_scaling
        result['ENERGY_PGP_STORAGE'] = energy_pgp_storage/numerics_demand_scaling
        
    if 'UNMET_DEMAND' in system_components:
        result['DISPATCH_UNMET_DEMAND'] = np.array(dispatch_unmet_demand.value).flatten()/numerics_demand_scaling
    else:
        result['DISPATCH_UNMET_DEMAND'] = dispatch_unmet_demand/numerics_demand_scaling

    return result
  