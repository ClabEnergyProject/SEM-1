#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
File name: Save_Basic_Results.py
    Save basic results from Core_Model as pickle and .csv files.

Current version: my180628-const-nuc-A
    Modified from SEM-1-my180627 for nuclear vs. renewables analysis.
    Nuclear, wind, and solar represented by Formulation A (previously Formulation 2A') with nonzero curtailment (generic equations).
    Note: This version is the same as SEM-1-my180628 but renamed to avoid confusion.

Updates (from SEM-1-my180628):
    (a) separated curtailment of solar, wind, and nuclear
        - checked results against -my180627, system cost and total curtailment in agreement
    
"""

#%% import modules

import os
import numpy as np
import csv
import datetime
import contextlib
import pickle

#%% merge two dictionaries
def merge_two_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns none
    return z

#%% save results in pickle and .csv files
def save_basic_results(global_dic, case_dic_list, result_list ):
    
    verbose = global_dic['VERBOSE']
    if verbose:
        print 'Save_Basic_Results.py: Pickling raw results'
    # save results in pickle file
    pickle_raw_results(global_dic, case_dic_list, result_list )
    
    if verbose:
        print 'Save_Basic_Results.py: Saving vector results'
    # save time-series results in series of .csv files
    save_vector_results_as_csv(global_dic, case_dic_list, result_list )
    
    if verbose:
        print 'Save_Basic_Results.py: Saving key scalar results'
    # save key results in summary .csv file (time-series results are averaged)
    scalar_names,scalar_table = postprocess_key_scalar_results(global_dic, case_dic_list, result_list )
    
    return scalar_names,scalar_table

#%% save results in pickle file

def pickle_raw_results( global_dic, case_dic_list, result_list ):
    
    output_path = global_dic['OUTPUT_PATH']
    global_name = global_dic['GLOBAL_NAME']
    output_folder = output_path + '/' + global_name
    output_file_name = global_name + '.pickle'
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    with open(output_folder + "/" + output_file_name, 'wb') as db:
        pickle.dump([global_dic,case_dic_list,result_list], db, protocol=pickle.HIGHEST_PROTOCOL)

#%% save time-series results in series of .csv files

def save_vector_results_as_csv( global_dic, case_dic_list, result_list ):
    
    output_path = global_dic['OUTPUT_PATH']
    global_name = global_dic['GLOBAL_NAME']
    output_folder = output_path + '/' + global_name

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for idx in range(len(result_list)):
        
        case_dic = case_dic_list[idx]
        if len(case_dic['WIND_SERIES']) == 0:
            case_dic['WIND_SERIES'] = ( 0.*np.array(case_dic['DEMAND_SERIES'])).tolist()
        if len(case_dic['SOLAR_SERIES']) == 0:
            case_dic['WIND_SERIES'] = ( 0.*np.array(case_dic['DEMAND_SERIES'])).tolist()
            
        result = result_list[idx]
        
        header_list = []
        series_list = []
        
        header_list += ['demand (kW)']
        series_list.append( case_dic['DEMAND_SERIES'] )
        
        header_list += ['solar (kW)']   # input solar capacity factors
        series_list.append( np.array(case_dic['SOLAR_SERIES'])*result['CAPACITY_SOLAR'] )

        header_list += ['wind (kW)']    # input wind capacity factors
        series_list.append( np.array(case_dic['WIND_SERIES'])*result['CAPACITY_WIND'] )
        
        header_list += ['dispatch solar (kW)']
        series_list.append( result['DISPATCH_SOLAR'].flatten() )     
        
        header_list += ['dispatch wind (kW)']
        series_list.append( result['DISPATCH_WIND'].flatten() )
        
        header_list += ['dispatch natgas (kW)']
        series_list.append( result['DISPATCH_NATGAS'].flatten() )
        
        header_list += ['dispatch nuclear (kW)']
        series_list.append( result['DISPATCH_NUCLEAR'].flatten() )
        
        header_list += ['dispatch to storage (kW)']
        series_list.append( result['DISPATCH_TO_STORAGE'].flatten() )
        
        header_list += ['dispatch from storage (kW)']
        series_list.append( result['DISPATCH_FROM_STORAGE'].flatten() )

        header_list += ['energy storage (kWh)']
        series_list.append( result['ENERGY_STORAGE'].flatten() )
      
        header_list += ['dispatch to PGP storage (kW)']
        series_list.append( result['DISPATCH_TO_PGP_STORAGE'].flatten() )
        
        header_list += ['dispatch from PGP storage (kW)']
        series_list.append( result['DISPATCH_FROM_PGP_STORAGE'].flatten() )

        header_list += ['energy PGP storage (kWh)']
        series_list.append( result['ENERGY_PGP_STORAGE'].flatten() )
        
        header_list += ['curtailment solar (kW)']
        series_list.append( result['CURTAILMENT_SOLAR'].flatten() )
        
        header_list += ['curtailment wind (kW)']
        series_list.append( result['CURTAILMENT_WIND'].flatten() )

        header_list += ['curtailment nuclear (kW)']
        series_list.append( result['CURTAILMENT_NUCLEAR'].flatten() )
        
        header_list += ['dispatch unmet demand (kW)']
        series_list.append( result['DISPATCH_UNMET_DEMAND'].flatten() )
         
        output_file_name = case_dic['CASE_NAME']
    
        with contextlib.closing(open(output_folder + "/" + output_file_name + '.csv', 'wb')) as output_file:
            writer = csv.writer(output_file)
            writer.writerow(header_list)
            writer.writerows((np.asarray(series_list)).transpose())
            output_file.close()

#%% save key results in summary .csv file (time-series results are averaged)

def postprocess_key_scalar_results( global_dic, case_dic_list, result_list ):
    
    verbose = global_dic['VERBOSE']
    
    combined_dic = map(merge_two_dicts,case_dic_list,result_list)
    
    scalar_names = [
    
            'case name',
            
            # assumptions: capacity costs
            'capacity cost natgas ($/kW/h)',
            'capacity cost solar ($/kW/h)',
            'capacity cost wind ($/kW/h)',
            'capacity cost nuclear ($/kW/h)',
            'capacity cost storage ($/kWh/h)',
            'capacity cost pgp storage ($/kWh/h)',
            
            # assumptions: dispatch costs
            'dispatch cost natgas ($/kWh)',
            'dispatch cost solar ($/kWh)',
            'dispatch cost wind ($/kWh)',
            'dispatch cost nuclear ($/kWh)',
            'dispatch cost to storage ($/kWh)',
            'dispatch cost from storage ($/kWh)',
            'dispatch cost to pgp storage ($/kWh)',
            'dispatch cost from pgp storage ($/kWh)',
            'dispatch cost unmet demand ($/kWh)',
            
            # assumptions: storage efficiencies
            'storage charging efficiency',
            'storage charging time (h)',
            'storage decay rate (1/h)',
            'pgp storage charging efficiency',
            
            # inputs: averaged demand and wind and solar capacity factors
            'demand (kW)',
            'solar capacity (kW)',
            'wind capacity (kW)',
            
            # results: capacity, system cost, problem status
            'capacity natgas (kW)',
            'capacity solar (kW)',
            'capacity wind (kW)',
            'capacity nuclear (kW)',
            'capacity storage (kWh)',
            'capacity pgp storage (kWh)',
            'capacity pgp fuel cell (kW)',
            'system cost ($/kW/h)',     # assuming demand normalized to 1 kW
            'problem status',
            
            # results: averaged dispatch and curtailment
            'dispatch natgas (kW)',
            'dispatch solar (kW)',
            'dispatch wind (kW)',
            'dispatch nuclear (kW)',
            'dispatch to storage (kW)',
            'dispatch from storage (kW)',
            'energy storage (kWh)',
            'dispatch to pgp storage (kW)',
            'dispatch from pgp storage (kW)',
            'energy pgp storage (kWh)',
            'curtailment solar (kW)',
            'curtailment wind (kW)',
            'curtailment nuclear (kW)',
            'dispatch unmet demand (kW)'
            
            ]

    scalar_table = [
            [       d['CASE_NAME'],
             
                    # assumptions: capacity costs                    
                    d['CAPACITY_COST_NATGAS'],
                    d['CAPACITY_COST_SOLAR'],
                    d['CAPACITY_COST_WIND'],
                    d['CAPACITY_COST_NUCLEAR'],
                    d['CAPACITY_COST_STORAGE'],
                    d['CAPACITY_COST_PGP_STORAGE'],
                    
                    # assumptions: dispatch costs
                    d['DISPATCH_COST_NATGAS'],
                    d['DISPATCH_COST_SOLAR'],
                    d['DISPATCH_COST_WIND'],
                    d['DISPATCH_COST_NUCLEAR'],
                    d['DISPATCH_COST_TO_STORAGE'],
                    d['DISPATCH_COST_FROM_STORAGE'],
                    d['DISPATCH_COST_TO_PGP_STORAGE'],
                    d['DISPATCH_COST_FROM_PGP_STORAGE'],
                    d['DISPATCH_COST_UNMET_DEMAND'],
                    
                    # assumptions: storage efficiencies
                    d['STORAGE_CHARGING_EFFICIENCY'],
                    d['STORAGE_CHARGING_TIME'],
                    d['STORAGE_DECAY_RATE'],
                    d['PGP_STORAGE_CHARGING_EFFICIENCY'],
                    
                    # inputs: averaged demand and wind and solar capacity factors
                    np.average(d['DEMAND_SERIES']),
                    np.average(d['SOLAR_SERIES']),
                    np.average(d['WIND_SERIES']),
                    
                    # results: capacity, system cost, problem status
                    d['CAPACITY_NATGAS'],
                    d['CAPACITY_SOLAR'],
                    d['CAPACITY_WIND'],
                    d['CAPACITY_NUCLEAR'],
                    d['CAPACITY_STORAGE'],
                    d['CAPACITY_PGP_STORAGE'],
                    d['CAPACITY_PGP_FUEL_CELL'],
                    d['SYSTEM_COST'],
                    d['PROBLEM_STATUS'],
                    
                    # results: averaged dispatch
                    np.average(d['DISPATCH_NATGAS']),
                    np.average(d['DISPATCH_SOLAR']),
                    np.average(d['DISPATCH_WIND']),
                    np.average(d['DISPATCH_NUCLEAR']),
                    np.average(d['DISPATCH_TO_STORAGE']),
                    np.average(d['DISPATCH_FROM_STORAGE']),
                    np.average(d['ENERGY_STORAGE']),
                    np.average(d['DISPATCH_TO_PGP_STORAGE']),
                    np.average(d['DISPATCH_FROM_PGP_STORAGE']),
                    np.average(d['ENERGY_PGP_STORAGE']),
                    np.average(d['CURTAILMENT_SOLAR']),
                    np.average(d['CURTAILMENT_WIND']),
                    np.average(d['CURTAILMENT_NUCLEAR']),
                    np.average(d['DISPATCH_UNMET_DEMAND'])
             ]
             
            for d in combined_dic
            ]
            
    output_path = global_dic['OUTPUT_PATH']
    global_name = global_dic['GLOBAL_NAME']
    output_folder = output_path + "/" + global_name
    today = datetime.datetime.now()
    todayString = str(today.year) + str(today.month).zfill(2) + str(today.day).zfill(2) + '_' + \
        str(today.hour).zfill(2) + str(today.minute).zfill(2) + str(today.second).zfill(2)
    output_file_name = global_name + '_' + todayString
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    with contextlib.closing(open(output_folder + "/" + output_file_name +'.csv', 'wb')) as output_file:
        writer = csv.writer(output_file)
        writer.writerow(scalar_names)
        writer.writerows(scalar_table)
        output_file.close()
        
    if verbose: 
        print 'file written: ' + output_file_name + '.csv'
    
    return scalar_names,scalar_table
        