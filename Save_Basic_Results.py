# -*- coding: utf-8 -*-

"""

Save_Basic_Results.py

save basic results for the simple energy model
    
"""

# -----------------------------------------------------------------------------


import os
import numpy as np
import csv
import datetime
import contextlib
import pickle

# Core function
#   Linear programming
#   Output postprocessing

#    case_dic = { 
#            'input_folder':input_folder, 
#            'output_folder':output_folder, 
#            'output_file_name':base_case_switch + "_" + case_switch+".csv",
#            'base_case_switch':base_case_switch,
#            'case_switch':case_switch
#            }
def pickle_raw_results( global_dic, case_dic_list, result_list ):
    
    output_path = global_dic['OUTPUT_PATH']
    global_name = global_dic['GLOBAL_NAME']
    output_folder = output_path + '/' + global_name
    output_file_name = global_name + '.pickle'
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    with open(output_folder + "/" + output_file_name, 'wb') as db:
        pickle.dump([global_dic,case_dic_list,result_list], db, protocol=pickle.HIGHEST_PROTOCOL)

def merge_two_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z

def save_basic_results(global_dic, case_dic_list, result_list ):
    
    verbose = global_dic['VERBOSE']
    if verbose:
        print 'Save_Basic_Results.py: Pickling raw results'
    # put raw results in file for later analysis
    pickle_raw_results(global_dic, case_dic_list, result_list )
    
    if verbose:
        print 'Save_Basic_Results.py: saving vector results'
    # Do the most basic scalar analysis
    save_vector_results_as_csv(global_dic, case_dic_list, result_list )
    
    if verbose:
        print 'Save_Basic_Results.py: saving key scalar results'
    # Do the most basic scalar analysis
    scalar_names,scalar_table = postprocess_key_scalar_results(global_dic, case_dic_list, result_list )
    
    return scalar_names,scalar_table

# save results by case
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
        
        header_list += ['Time (hr)']
        series_list.append( np.arange(len(case_dic['DEMAND_SERIES'])))
        
        header_list += ['demand (kW)']
        series_list.append( case_dic['DEMAND_SERIES'] )
        
        header_list += ['solar capacity factor (kW)']
        series_list.append( np.array(case_dic['SOLAR_SERIES']))
        
        header_list += ['dispatch_solar (kW per unit deployed)']
        series_list.append( result['DISPATCH_SOLAR'].flatten() )     
        
        header_list += ['wind capacity factor (kW per unit deployed)']
        series_list.append( np.array(case_dic['WIND_SERIES']))

        header_list += ['dispatch wind (kW)']
        series_list.append( result['DISPATCH_WIND'].flatten() )
        
        header_list += ['dispatch_natgas (kW)']
        series_list.append( result['DISPATCH_NATGAS'].flatten() )
        
        header_list += ['dispatch_nuclear (kW)']
        series_list.append( result['DISPATCH_NUCLEAR'].flatten() )
        
        header_list += ['dispatch_to_storage (kW)']
        series_list.append( result['DISPATCH_TO_STORAGE'].flatten() )
        
        header_list += ['dispatch_from_storage (kW)']
        series_list.append( result['DISPATCH_FROM_STORAGE'].flatten() )  # THere is no FROM in dispatch results

        header_list += ['energy storage (kWh)']
        series_list.append( result['ENERGY_STORAGE'].flatten() )
      
        header_list += ['dispatch_to_pgp_storage (kW)']
        series_list.append( result['DISPATCH_TO_PGP_STORAGE'].flatten() )
        
        header_list += ['dispatch_pgp_storage (kW)']
        series_list.append( result['DISPATCH_FROM_PGP_STORAGE'].flatten() )

        header_list += ['energy pgp storage (kWh)']
        series_list.append( result['ENERGY_PGP_STORAGE'].flatten() )
        
        header_list += ['dispatch_unmet_demand (kW)']
        series_list.append( result['DISPATCH_UNMET_DEMAND'].flatten() )
         
        output_file_name = case_dic['CASE_NAME']
    
        with contextlib.closing(open(output_folder + "/" + output_file_name + '.csv', 'wb')) as output_file:
            writer = csv.writer(output_file)
            writer.writerow(header_list)
            writer.writerows((np.asarray(series_list)).transpose())
            output_file.close()
 
# save scalar results for all cases
def postprocess_key_scalar_results( global_dic, case_dic_list, result_list ):
    
    verbose = global_dic['VERBOSE']
    
    combined_dic = map(merge_two_dicts,case_dic_list,result_list)
    
    scalar_names = [
            'case name',
            'capacity_cost_natgas ($/kW/h)',
            'capacity_cost_solar ($/kW/h)',
            'capacity_cost_wind ($/kW/h)',
            'capacity_cost_nuclear ($/kW/h)',
            'capacity_cost_storage (($/h)/kWh)',
            'capacity_cost_pgp_storage (($/h)/kWh)',
            
            'dispatch_cost_natgas ($/kWh)',
            'dispatch_cost_solar ($/kWh)',
            'dispatch_cost_wind ($/kWh)',
            'dispatch_cost_nuclear ($/kWh)',
            'dispatch_cost_to_storage ($/kWh)',
            'dispatch_cost_storage ($/kWh)',
            'dispatch_cost_to_pgp_storage ($/kWh)',
            'dispatch_cost_pgp_storage ($/kWh)',
            'dispatch_cost_unmet_demand ($/kWh)',
            
            'storage_charging_efficiency',
            'storage_charging_time (h)',
            'storage_decay_rate (1/h)',
            'pgp_storage_charging_efficiency',
            
            'mean demand (kW)',
            'capacity factor wind series (kW)',
            'capacity factor solar series (kW)',
            
            'capacity_natgas (kW)',
            'capacity_solar (kW)',
            'capacity_wind (kW)',
            'capacity_nuclear (kW)',
            'capacity_storage (kWh)',
            'capacity_pgp_storage (kWh)',
            'capacity_to_pgp_storage (kW)',
            'capacity_from_pgp_storage (kW)',
            'system_cost ($/kW/h)', # assuming demand normalized to 1 kW
            'problem_status',
            
            'dispatch_natgas (kW)',
            'dispatch_solar (kW)',
            'dispatch_wind (kW)',
            'dispatch_nuclear (kW)',
            'dispatch_to_storage (kW)',
            'dispatch_from_storage (kW)',
            'energy_storage (kWh)',
            'dispatch_to_pgp_storage (kW)',
            'dispatch_pgp_storage (kW)',
            'energy_pgp_storage (kWh)',
            'dispatch_unmet_demand (kW)'
            
            
            ]

    scalar_table = [
            [       d['CASE_NAME'],
             
                    # assumptions
                    
                    d['CAPACITY_COST_NATGAS'],
                    d['CAPACITY_COST_SOLAR'],
                    d['CAPACITY_COST_WIND'],
                    d['CAPACITY_COST_NUCLEAR'],
                    d['CAPACITY_COST_STORAGE'],
                    d['CAPACITY_COST_PGP_STORAGE'],
                    
                    d['DISPATCH_COST_NATGAS'],
                    d['DISPATCH_COST_SOLAR'],
                    d['DISPATCH_COST_WIND'],
                    d['DISPATCH_COST_NUCLEAR'],
                    d['DISPATCH_COST_TO_STORAGE'],
                    d['DISPATCH_COST_FROM_STORAGE'],
                    d['DISPATCH_COST_TO_PGP_STORAGE'],
                    d['DISPATCH_COST_FROM_PGP_STORAGE'],
                    d['DISPATCH_COST_UNMET_DEMAND'],
                    
                    d['STORAGE_CHARGING_EFFICIENCY'],
                    d['STORAGE_CHARGING_TIME'],
                    d['STORAGE_DECAY_RATE'],
                    d['PGP_STORAGE_CHARGING_EFFICIENCY'],
                    
                    # mean of time series assumptions
                    np.average(d['DEMAND_SERIES']),
                    np.average(d['WIND_SERIES']),
                    np.average(d['SOLAR_SERIES']),
                    
                    # scalar results
                    
                    d['CAPACITY_NATGAS'],
                    d['CAPACITY_SOLAR'],
                    d['CAPACITY_WIND'],
                    d['CAPACITY_NUCLEAR'],
                    d['CAPACITY_STORAGE'],
                    d['CAPACITY_PGP_STORAGE'],
                    d['CAPACITY_TO_PGP_STORAGE'],
                    d['CAPACITY_FROM_PGP_STORAGE'],
                    d['SYSTEM_COST'],
                    d['PROBLEM_STATUS'],
                    
                    # mean of time series results                
                                
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
    
def out_csv(output_folder,output_file_name,names,table,verbose):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    with contextlib.closing(open(output_folder + "/" + output_file_name +'.csv', 'wb')) as output_file:
        writer = csv.writer(output_file)
        writer.writerow(names)
        writer.writerows(table)
        output_file.close()
        
    if verbose: 
        print 'file written: ' + output_file_name + '.csv'
    


    