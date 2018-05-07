# -*- codiNatgas: utf-8 -*-
"""
This code reads a file called 'case_input.csv' which is assumed to exist in the directory in which the code is running.

It generates a result containing <assumption_list>
    
<assumption_list> is a list of dictionaries. Each element in that list corresponds to a different case to be run.

Each dictionary in <assumption_list> ALWAYS contains:
    
    'system_components' -- list of components, choices are: 'wind','solar', 'natgas','nuclear','storage','unmet'
    'root_path' -- path to data files
    'demand_series' -- time series of demand data
    'output_directory' -- string containing name of output directory
    
Each dictionary in <assumption_list> OPTIONALLY contains:
    
            'fix_cost_natgas' -- scalar
            'fix_cost_nuclear' -- scalar
            'fix_cost_wind' -- scalar
            'fix_cost_solar' -- scalar
            'fix_cost_storage' -- scalar
            'var_cost_natgas' -- scalar
            'var_cost_nuclear' -- scalar
            'var_cost_wind' -- scalar
            'var_cost_solar' -- scalar
            'var_cost_storage' -- scalar
            'var_cost_dispatch_to_storage' -- scalar
            'var_cost_dispatch_from_storage' -- scalar
            'var_cost_unmet_demand' -- scalar
            'storage_charging_efficiency' -- scalar
            'wind_series' -- time series of wind capacity data
            'solar_series' -- time series of solar capacity data

"""

import csv
import sys
import numpy as np
import itertools,functools,operator

import datetime



#%%
def import_case_input(case_input_path_filename):
    # Import case_input.csv file from local directory.
    # return 2 objects: param_list, and case_list
    # <param_list> contains information that is true for all cases in the set of runs
    # <case_list> contains information that is true for a particular case
    
    # first open the file and define the reader
    f = open(case_input_path_filename)
    rdr = csv.reader(f)
    
    #Throw away all lines up to and include the line that has "BEGIN_GLOBAL_DATA" in the first cell of the line
    while True:
        line = rdr.next()
        if line[0] == "BEGIN_GLOBAL_DATA":
            break
    
    # Now take all non-blank lines until "BEGIN_CASE_DATA"
    global_data = []
    while True:
        line = rdr.next()
        if line[0] == "BEGIN_CASE_DATA":
            break
        if line[0] != "":
            global_data.append(line[0:2])
            
    # Now take all non-blank lines until "END_DATA"
    case_data = []
    while True:
        line = rdr.next()
        if line[0] == "END_DATA":
            break
        if line[0] != "":
            case_data.append(line)
            
    return global_data,case_data

def read_csv_dated_data_file(start_year,start_month,start_day,start_hour,
                             end_year,end_month,end_day,end_hour,
                             data_path, data_filename):
    
    if data_path.endswith('/'):
        path_filename = data_path + data_filename
    else:
        path_filename = data_path + '/' + data_filename
    print path_filename
    print data_path
    print data_filename
    data = []
    with open(path_filename) as fin:
        data_reader = csv.reader(fin)
        for row in data_reader:
            data.append(row)

    start_hour = start_hour + 100 * (start_day + 100 * (start_month + 100* start_year)) 
    end_hour = end_hour + 100 * (end_day + 100 * (end_month + 100* end_year)) 

    data_array = np.array(data[1:]) # throw away first header row 
    hour_num = data_array[:,3] + 100 * (data_array[:,2] + 100 * (data_array[:,1] + 100* data_array[:,0]))   

    series = [item[1] for item in zip(hour_num,data_array[:,4]) if item[0]>= start_hour and item[0] <= end_hour]
    
    return series    

def preprocess_input(case_input_path_filename):
    # This is the highest level function that reads in the case input file
    # and generated <assumption_list> from this input.
        
    # -----------------------------------------------------------------------------
    # Recognized keywords in case_input.csv file
    
    keywords_logical = map(str.upper,
            ["verbose"]
            )

    keywords_str = map(str.upper,
            ["data_path","demand_file",
             "solar_capacity_file","wind_capacity_file","output_path"]
            )
    
    keywords_real = map(str.upper,
            ["end_day","end_hour","end_month",
            "end_year","fix_cost_natgas","fix_cost_solar","fix_cost_wind",
            "fix_cost_nuclear","fix_cost_storage",
            "start_day","start_hour","start_month",
            "start_year","storage_charging_efficiency",
            "var_cost_dispatch_from_storage","var_cost_dispatch_to_storage",
            "var_cost_natgas","var_cost_solar","var_cost_storage",
            "var_cost_wind","var_cost_nuclear"]
            )
    
    # -----------------------------------------------------------------------------
    # Read in case data file
    
    global_data, case_data = import_case_input(case_input_path_filename)

    # -----------------------------------------------------------------------------
    # the basic logic here is that if a keyword appears in the "global"
    # section, then it is used for all cases if it is used in the "case" section
    # then it applies to that particular case.
    
    
    # Parse global data
    global_dic = {}
    for list_item in global_data:
        test_key = str.upper(list_item[0])
        test_value = list_item[1]
        print list_item
        if test_key in keywords_str:
            global_dic[test_key] = test_value
            print test_key
            print test_value
        elif test_key in keywords_real:
            global_dic[test_key] = float(test_value)
        elif test_key in keywords_logical:
            global_dic[test_key] = bool(test_value)
            
    case_transpose = map(list,zip(*case_data)) # transpose list of lists.
    # Note that the above line could cause problems if not all numbers are
    # entered uniformly in the case input file.
    
    # Now each element of case_transpose is the potential keyword followed by data
    case_dic = {}
    for list_item in case_transpose:
        test_key = str.upper(list_item[0])
        test_values = list_item[1:]
        if test_key in keywords_str:
            print test_key
            print test_values
            global_dic[test_key] = test_values
        elif test_key in keywords_real:
            global_dic[test_key] = map(float,test_values)
        elif test_key in keywords_logical:
            global_dic[test_key] = map(bool,test_values)
    
    if not set(global_dic.keys()).isdisjoint(case_dic.keys()):
        sys.exit( "Warning:  global keywords overlap with case keywords")
    
    # Number of cases to run is number of rows in case input file.
    num_cases = len(case_data) - 1 # the 1 is for the keyword row
    case_dic['NUM_CASES'] = num_cases
    
    # now add global variables to case_dic
    for keyword in global_dic.keys():
        case_dic[keyword] = [global_dic[keyword] for i in range(num_cases)] # replicate lists

    print case_dic['DATA_PATH']
    
    # define all keywords in dictionary, but set to -1 if not present    
    dummy = [-1 for i in range(num_cases)]
    for keyword in list(set(keywords_real).difference(case_dic.keys())):
        case_dic[keyword] = dummy
    
    # ok, now we have everything from the case_input file in case_dic.
    # Let's add the other things we need. First, we will see what system components
    # are used in each case.
    
    # for wind, solar, and demand, we also need to get the relevant demand files
    
    solar_series_list = []
    wind_series_list = []
    demand_series_list = []
    list_of_component_lists = []
    
    have_keys = case_dic.keys()
    for case_index in range(num_cases):
        
        # first read in demand series (which must exist)
        demand_series_list.append(
            read_csv_dated_data_file(
                    case_dic['START_YEAR'][case_index],
                    case_dic['START_MONTH'][case_index],
                    case_dic['START_DAY'][case_index],
                    case_dic['START_HOUR'][case_index],
                    case_dic['END_YEAR'][case_index],
                    case_dic['END_MONTH'][case_index],
                    case_dic['END_DAY'][case_index],
                    case_dic['END_HOUR'][case_index],
                    case_dic['DATA_PATH'][case_index],
                    case_dic['DEMAND_FILE'][case_index]
                    )
            )
            
        # check on each technology one by one
        component_list = []
        if 'FIX_COST_SOLAR' in have_keys:
            if case_dic['FIX_COST_SOLAR'][case_index] >= 0:
                component_list.append('SOLAR')
                solar_series_list.append(
                        read_csv_dated_data_file(
                                case_dic['START_YEAR'][case_index],
                                case_dic['START_MONTH'][case_index],
                                case_dic['START_DAY'][case_index],
                                case_dic['START_HOUR'][case_index],
                                case_dic['END_YEAR'][case_index],
                                case_dic['END_MONTH'][case_index],
                                case_dic['END_DAY'][case_index],
                                case_dic['END_HOUR'][case_index],
                                case_dic['DATA_PATH'][case_index],
                                case_dic['SOLAR_CAPACITY_FILE'][case_index]
                                )
                        )
        else:
            solar_series_list.append([])
                        
        if 'FIX_COST_WIND' in have_keys:
            if case_dic['FIX_COST_WIND'][case_index] >= 0:
                component_list.append('WIND')
                solar_series_list.append(
                        read_csv_dated_data_file(
                                case_dic['START_YEAR'][case_index],
                                case_dic['START_MONTH'][case_index],
                                case_dic['START_DAY'][case_index],
                                case_dic['START_HOUR'][case_index],
                                case_dic['END_YEAR'][case_index],
                                case_dic['END_MONTH'][case_index],
                                case_dic['END_DAY'][case_index],
                                case_dic['END_HOUR'][case_index],
                                case_dic['DATA_PATH'][case_index],
                                case_dic['WIND_CAPACITY_FILE'][case_index]
                                )
                        )
        else:
            wind_series_list.append([])
                                                
        if 'FIX_COST_NUCLEAR' in have_keys:
            if case_dic['FIX_COST_NUCLEAR'][case_index] >= 0:
                component_list.append('NUCLEAR')
                                                
        if 'FIX_COST_NATGAS' in have_keys:
            if case_dic['FIX_COST_NATGAS'][case_index] >= 0:
                component_list.append('NATGAS')
                                                
        if 'FIX_COST_STORAGE' in have_keys:
            if case_dic['FIX_COST_STORAGE'][case_index] >= 0:
                component_list.append('STORAGE')
                
        list_of_component_lists.append(component_list)
        
    case_dic['DEMAND_SERIES'] = demand_series_list
    case_dic['WIND_SERIES'] = wind_series_list
    case_dic['SOLAR_SERIES'] = solar_series_list
    case_dic['COMPONENTS'] = component_list
                               
    return case_dic

             
