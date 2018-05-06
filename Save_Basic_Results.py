#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""

File name: Core_Model.py

Idealized energy system models

Spatial scope: U.S.
Data: Matt Shaner's paper with reanalysis data and U.S. demand.

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


import os
import numpy as np
import csv
import shelve
import contextlib
import pickle

# Core function
#   Linear programming
#   Output postprocessing

#    file_info = { 
#            'input_folder':input_folder, 
#            'output_folder':output_folder, 
#            'output_file_name':base_case_switch + "_" + case_switch+".csv",
#            'base_case_switch':base_case_switch,
#            'case_switch':case_switch
#            }

def merge_two_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z

def save_basic_results(
        file_info,
        time_series,
        assumption_list,
        result_list,
        verbose
        ):
    
    # put raw results in file for later analysis
    pickle_raw_results(
        file_info,
        time_series,
        assumption_list,
        result_list,
        verbose
        )
    
    # Do the most basic scalar analysis
    save_vector_results_as_csv(
        file_info,
        time_series,
        result_list,
        verbose
        )
    
    # Do the most basic scalar analysis
    scalar_names,scalar_table = postprocess_key_scalar_results(
        file_info,
        time_series,
        assumption_list,
        result_list,
        verbose
        )
    
    return scalar_names,scalar_table

def pickle_raw_results(
        file_info,
        time_series,
        assumption_list,
        result_list,
        verbose
        ):
    output_folder = file_info['output_folder']
    output_file_name = file_info['case_switch']+'.pickle'
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    with open(output_folder + "/" + output_file_name, 'wb') as db:
        pickle.dump([file_info,time_series,assumption_list,result_list], db, protocol=pickle.HIGHEST_PROTOCOL)

    
    if verbose:
        print 'data pickled to '+output_folder + "/" + output_file_name

#def unpickle_raw_results(
#        file_path_name,
#        verbose
#        ):
#    
#    with open(file_path_name, 'rb') as db:
#       file_info, time_series, assumption_list, result_list = pickle.load (db)
#    
#    if verbose:
#        print 'data unpickled from '+file_path_name
#    
#    return file_info, time_series, assumption_list, result_list

def save_vector_results_as_csv(
        file_info,
        time_series,
        result_list,
        verbose
        ):
    
    output_folder = file_info['output_folder']
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    num_time_periods = result_list[0]['dispatch_natgas'].size
    outarray = np.zeros((1+num_time_periods,8))

    for idx in range(len(result_list)):
        output_file_name = file_info['output_file_name']+'_series_'+  str(idx).zfill(3)
        
        result = result_list[idx]
        
        header_list = []
        series_list = []
        
        header_list += ['demand (kW)']
        series_list.append( time_series['demand_series'] )
        
        header_list += ['wind (kW)']
        series_list.append( time_series['wind_series'] )
        
        header_list += ['solar (kW)']
        series_list.append( time_series['solar_series'] )
        
        header_list += ['dispatch_natgas (kW)']
        series_list.append( result['dispatch_natgas'].flatten() )
        
        header_list += ['dispatch_solar (kW)']
        series_list.append( result['dispatch_solar'].flatten() )
        
        header_list += ['dispatch wind (kW)']
        series_list.append( result['dispatch_wind'].flatten() )
        
        header_list += ['dispatch_nuclear (kW)']
        series_list.append( result['dispatch_nuclear'].flatten() )
        
        header_list += ['dispatch_to_storage (kW)']
        series_list.append( result['dispatch_to_storage'].flatten() )
        
        header_list += ['dispatch_from_storage (kW)']
        series_list.append( result['dispatch_from_storage'].flatten() )

        header_list += ['energy storage (kWh)']
        series_list.append( result['energy_storage'].flatten() )
        
        header_list += ['dispatch_curtailment (kW)']
        series_list.append( result['dispatch_curtailment'].flatten() )
        
        header_list += ['dispatch_unmet_demand (kW)']
        series_list.append( result['dispatch_unmet_demand'].flatten() )

        out_array = np.array(series_list)
        
        with contextlib.closing(open(output_folder + "/" + output_file_name + '.csv', 'wb')) as output_file:
            writer = csv.writer(output_file)
            writer.writerow(header_list)
            writer.writerows((np.asarray(series_list)).transpose())
            output_file.close()
        
        if verbose: 
            print 'file written: ' + output_file_name +'.csv'

   
def postprocess_key_scalar_results(
        file_info,
        time_series,
        assumption_list,
        result_list,
        verbose
        ):
    
    combined_dic = map(merge_two_dicts,assumption_list,result_list)
    
    scalar_names = [
            'fix_cost_natgas ($/kW/h)',
            'fix_cost_solar ($/kW/h)',
            'fix_cost_wind ($/kW/h)',
            'fix_cost_nuclear ($/kW/h)',
            'fix_cost_storage ($/kW/h)',
            
            'var_cost_natgas ($/kWh)',
            'var_cost_solar ($/kWh)',
            'var_cost_wind ($/kWh)',
            'var_cost_nuclear ($/kWh)',
            'var_cost_storage ($/kWh/h)',
            'var_cost_dispatch_to_storage ($/kWh)',
            'var_cost_dispatch_from_storage ($/kWh)',
            'var_cost_unmet_demand ($/kWh)',
            
            'storage_charging_efficiency',
            
            'demand flag',
            'demand (kW)',
            'wind capacity (kW)',
            'solar capacity (kW)',
            
            'capacity_natgas (kW)',
            'capacity_solar (kW)',
            'capacity_wind (kW)',
            'capacity_nuclear (kW)',
            'capacity_storage (kW)',
            'system_cost ($/kW/h)', # assuming demand normalized to 1 kW
            'problem_status',
            
            'dispatch_natgas (kW)',
            'dispatch_solar (kW)',
            'dispatch_wind (kW)',
            'dispatch_nuclear (kW)',
            'dispatch_to_storage (kW)',
            'dispatch_from_storage (kW)',
            'energy_storage (kWh)',
            'dispatch_curtailment (kW)',
            'dispatch_unmet_demand (kW)'
            
            
            ]

    num_time_periods = combined_dic[0]['dispatch_natgas'].size
    
    scalar_table = [
            [
                    # assumptions
                    
                    d['fix_cost_natgas'],
                    d['fix_cost_solar'],
                    d['fix_cost_wind'],
                    d['fix_cost_nuclear'],
                    d['fix_cost_storage'],
                    
                    d['var_cost_natgas'],
                    d['var_cost_solar'],
                    d['var_cost_wind'],
                    d['var_cost_nuclear'],
                    d['var_cost_storage'],
                    d['var_cost_dispatch_to_storage'],
                    d['var_cost_dispatch_from_storage'],
                    d['var_cost_unmet_demand'],
                    
                    d['storage_charging_efficiency'],
                    
                    # mean of time series assumptions
                    d['demand_flag'],
                    np.sum(time_series['demand_series'])/num_time_periods,
                    np.sum(time_series['solar_series'])/num_time_periods,
                    np.sum(time_series['wind_series'])/num_time_periods,
                    
                    # scalar results
                    
                    d['capacity_natgas'],
                    d['capacity_solar'],
                    d['capacity_wind'],
                    d['capacity_nuclear'],
                    d['capacity_storage'],
                    d['system_cost'],
                    d['problem_status'],
                    
                    # mean of time series results                
                                
                    np.sum(d['dispatch_natgas'])/num_time_periods,
                    np.sum(d['dispatch_solar'])/num_time_periods,
                    np.sum(d['dispatch_wind'])/num_time_periods,
                    np.sum(d['dispatch_nuclear'])/num_time_periods,
                    np.sum(d['dispatch_to_storage'])/num_time_periods,
                    np.sum(d['dispatch_from_storage'])/num_time_periods,
                    np.sum(d['energy_storage'])/num_time_periods,
                    np.sum(d['dispatch_curtailment'])/num_time_periods,
                    np.sum(d['dispatch_unmet_demand'])/num_time_periods
                    
                    
             ]
            for d in combined_dic
            ]
            
    output_folder = file_info['output_folder']
    output_file_name = file_info['output_file_name']
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    with contextlib.closing(open(output_folder + "/" + output_file_name +'.csv', 'wb')) as output_file:
        writer = csv.writer(output_file)
        writer.writerow(scalar_names)
        writer.writerows(scalar_table)
        output_file.close()
        
    if verbose: 
        print 'file written: ' + file_info['output_file_name']+'.csv'
    
    return scalar_names,scalar_table
    
def out_csv(output_folder,output_file_name,names,table,verbose):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    with contextlib.closing(open(output_folder + "/" + output_file_name +'.csv', 'wb')) as output_file:
        writer = csv.writer(output_file)
        writer.writerow(names)
        writer.writerows(table)
        output_file.close()
        
    if verbose: 
        print 'file written: ' + output_folder + "/" + output_file_name +'.csv'
    


    