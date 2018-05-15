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
    
            'CAPACITY_COST_natgas' -- scalar
            'CAPACITY_COST_nuclear' -- scalar
            'CAPACITY_COST_wind' -- scalar
            'CAPACITY_COST_solar' -- scalar
            'CAPACITY_COST_storage' -- scalar
            'DISPATCH_COST_natgas' -- scalar
            'DISPATCH_COST_nuclear' -- scalar
            'DISPATCH_COST_wind' -- scalar
            'DISPATCH_COST_solar' -- scalar
            'DISPATCH_COST_storage' -- scalar
            'DISPATCH_COST_dispatch_to_storage' -- scalar
            'DISPATCH_COST_dispatch_from_storage' -- scalar
            'DISPATCH_COST_unmet_demand' -- scalar
            'storage_charging_efficiency' -- scalar
            'wind_series' -- time series of wind capacity data
            'solar_series' -- time series of solar capacity data

"""

import csv
import sys
import numpy as np
import pickle




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
    
    # Now take all non-blank lines until "BEGIN_ALL_CASES_DATA" or "BEGIN_CASE_DATA"
    global_data = []
    while True:
        line = rdr.next()
        if line[0] == "BEGIN_ALL_CASES_DATA" or line[0] == 'BEGIN_CASE_DATA':
            break
        if line[0] != "":
            global_data.append(line[0:2])
            
    # Now take all non-blank lines until "BEGIN_CASE_DATA"
    all_cases_data = []
    if line[0] == 'BEGIN_ALL_CASES_DATA':
        while True:
            line = rdr.next()
            if line[0] == "BEGIN_CASE_DATA":
                break
            if line[0] != "":
                all_cases_data.append(line[0:2])
            
    # Now take all non-blank lines until "END_DATA"
    case_data = []
    while True:
        line = rdr.next()
        if line[0] == "END_DATA":
            break
        if line[0] != "":
            case_data.append(line)
            
    return global_data,all_cases_data,case_data

def read_csv_dated_data_file(start_year,start_month,start_day,start_hour,
                             end_year,end_month,end_day,end_hour,
                             data_path, data_filename):
    
    # turn dates into yyyymmddhh format for comparison.
    # Assumes all datasets are on the same time step and are not missing any data.
    start_hour = start_hour + 100 * (start_day + 100 * (start_month + 100* start_year)) 
    end_hour = end_hour + 100 * (end_day + 100 * (end_month + 100* end_year)) 
      
    path_filename = data_path + '/' + data_filename
    
    data = []
    with open(path_filename) as fin:
        # read to keyword "BEGIN_DATA" and then one more line (header line)
        data_reader = csv.reader(fin)
        
        #Throw away all lines up to and include the line that has "BEGIN_GLOBAL_DATA" in the first cell of the line
        while True:
            line = data_reader.next()
            if line[0] == "BEGIN_DATA":
                break
        # Now take the header row
        line = data_reader.next()
        
        # Now take all non-blank lines
        data = []
        while True:
            try:
                line = data_reader.next()
                if any(field.strip() for field in line):
                    data.append([int(line[0]),int(line[1]),int(line[2]),int(line[3]),float(line[4])])
                    # the above if clause was from: https://stackoverflow.com/questions/4521426/delete-blank-rows-from-csv
            except:
                break
            
    data_array = np.array(data) # make into a numpy object
    
    hour_num = data_array[:,3] + 100 * (data_array[:,2] + 100 * (data_array[:,1] + 100* data_array[:,0]))   
    

    series = [item[1] for item in zip(hour_num,data_array[:,4]) if item[0]>= start_hour and item[0] <= end_hour]
    
    return series    

def preprocess_input(case_input_path_filename):
    # This is the highest level function that reads in the case input file
    # and generated <assumption_list> from this input.
        
    # -----------------------------------------------------------------------------
    # Recognized keywords in case_input.csv file
    
    keywords_logical = map(str.upper,
            ["VERBOSE","POSTPROCESS"]
            )

    keywords_str = map(str.upper,
            ["DATA_PATH","DEMAND_FILE",
             "SOLAR_CAPACITY_FILE","WIND_CAPACITY_FILE","OUTPUT_PATH",
             "CASE_NAME","GLOBAL_NAME"]
            )
    
    keywords_real = map(str.upper,
            ["END_DAY","END_HOUR","END_MONTH",
            "END_YEAR","CAPACITY_COST_NATGAS","CAPACITY_COST_SOLAR","CAPACITY_COST_WIND",
            "CAPACITY_COST_NUCLEAR","CAPACITY_COST_STORAGE",
            "START_DAY","START_HOUR","START_MONTH",
            "START_YEAR","STORAGE_CHARGING_EFFICIENCY",
            "DISPATCH_COST_DISPATCH_FROM_STORAGE","DISPATCH_COST_DISPATCH_TO_STORAGE",
            "DISPATCH_COST_NATGAS","DISPATCH_COST_SOLAR","DISPATCH_COST_STORAGE",
            "DISPATCH_COST_WIND","DISPATCH_COST_NUCLEAR","DISPATCH_COST_UNMET_DEMAND"]
            )
    
    # -----------------------------------------------------------------------------
    # Read in case data file
    
    global_data, all_cases_data, case_data = import_case_input(case_input_path_filename)

    # -----------------------------------------------------------------------------
    # the basic logic here is that if a keyword appears in the "global"
    # section, then it is used for all cases if it is used in the "case" section
    # then it applies to that particular case.
        
    # Parse global data
    global_dic = {}
    for list_item in global_data:
        test_key = str.upper(list_item[0])
        test_value = list_item[1]
        if test_key in keywords_str:
            global_dic[test_key] = test_value
        elif test_key in keywords_real:
            global_dic[test_key] = float(test_value)
        elif test_key in keywords_logical:
            global_dic[test_key] = bool(test_value)
    
    verbose = global_dic['VERBOSE']
#    print global_dic
    if verbose:
        print "Preprocess_Input.py: Preparing case input"
        
    # Parse all_cases_dic data
    all_cases_dic = {}
    for list_item in all_cases_data:
        test_key = str.upper(list_item[0])
        test_value = list_item[1]
        if test_key in keywords_str:
            all_cases_dic[test_key] = test_value
        elif test_key in keywords_real:
            all_cases_dic[test_key] = float(test_value)
        elif test_key in keywords_logical:
            all_cases_dic[test_key] = bool(test_value)
    
#    print all_cases_data
#    print all_cases_dic        
    case_transpose = map(list,zip(*case_data)) # transpose list of lists.
    # Note that the above line could cause problems if not all numbers are
    # entered uniformly in the case input file.
        
    # Now each element of case_transpose is the potential keyword followed by data
    case_list_dic = {}
    for list_item in case_transpose:
        test_key = str.upper(list_item[0])
        test_values = list_item[1:]
        if test_key in keywords_str:
            case_list_dic[test_key] = test_values
        elif test_key in keywords_real:
            case_list_dic[test_key] = map(float,test_values)
        elif test_key in keywords_logical:
            case_list_dic[test_key] = map(bool,test_values)
 
#    print case_data
#    print 'before adding ', case_list_dic
    
    if not set(all_cases_dic.keys()).isdisjoint(case_list_dic.keys()):
        sys.exit( "Warning: all cases keywords overlap with case keywords")
    
    # Number of cases to run is number of rows in case input file.
    # Num cases and verbose are the only non-case specific inputs in case_list_dic.
    num_cases = len(case_data) - 1 # the 1 is for the keyword row
    global_dic['NUM_CASES'] = num_cases
    
    # now add global variables to case_list_dic
    for keyword in all_cases_dic.keys():
        case_list_dic[keyword] = [all_cases_dic[keyword] for i in range(num_cases)] # replicate lists

    # define all keywords in dictionary, but set to -1 if not present    
    dummy = [-1 for i in range(num_cases)]
    for keyword in list(set(keywords_real).difference(case_list_dic.keys())):
        case_list_dic[keyword] = dummy
    
    # ok, now we have everything from the case_input file in case_list_dic.
    # Let's add the other things we need. First, we will see what system components
    # are used in each case.
    
    # for wind, solar, and demand, we also need to get the relevant demand files
    

    
    have_keys = case_list_dic.keys()

    pFile = open('test.pickle','wb')
    pickle.dump(case_list_dic,pFile)
    pFile.close()
    
    solar_series_list = []
    wind_series_list = []
    demand_series_list = []

    for case_index in range(num_cases):
        if verbose:
            print 'Preprocess_Input.py: time series for ',case_list_dic['CASE_NAME'][case_index]
                
        # first read in demand series (which must exist)
        demand_series_list.append(
            read_csv_dated_data_file(
                    case_list_dic['START_YEAR'][case_index],
                    case_list_dic['START_MONTH'][case_index],
                    case_list_dic['START_DAY'][case_index],
                    case_list_dic['START_HOUR'][case_index],
                    case_list_dic['END_YEAR'][case_index],
                    case_list_dic['END_MONTH'][case_index],
                    case_list_dic['END_DAY'][case_index],
                    case_list_dic['END_HOUR'][case_index],
                    global_dic['DATA_PATH'],
                    case_list_dic['DEMAND_FILE'][case_index]
                    )
            )
            
        # check on each technology one by one

        if 'CAPACITY_COST_SOLAR' in have_keys:
            if case_list_dic['CAPACITY_COST_SOLAR'][case_index] >= 0:
                solar_series_list.append(
                        read_csv_dated_data_file(
                                case_list_dic['START_YEAR'][case_index],
                                case_list_dic['START_MONTH'][case_index],
                                case_list_dic['START_DAY'][case_index],
                                case_list_dic['START_HOUR'][case_index],
                                case_list_dic['END_YEAR'][case_index],
                                case_list_dic['END_MONTH'][case_index],
                                case_list_dic['END_DAY'][case_index],
                                case_list_dic['END_HOUR'][case_index],
                                global_dic['DATA_PATH'],
                                case_list_dic['SOLAR_CAPACITY_FILE'][case_index]
                                )
                        )
            else:
                solar_series_list.append([])
        else:
            solar_series_list.append([])
                        
        if 'CAPACITY_COST_WIND' in have_keys:
            if case_list_dic['CAPACITY_COST_WIND'][case_index] >= 0:
                wind_series_list.append(
                        read_csv_dated_data_file(
                                case_list_dic['START_YEAR'][case_index],
                                case_list_dic['START_MONTH'][case_index],
                                case_list_dic['START_DAY'][case_index],
                                case_list_dic['START_HOUR'][case_index],
                                case_list_dic['END_YEAR'][case_index],
                                case_list_dic['END_MONTH'][case_index],
                                case_list_dic['END_DAY'][case_index],
                                case_list_dic['END_HOUR'][case_index],
                                global_dic['DATA_PATH'],
                                case_list_dic['WIND_CAPACITY_FILE'][case_index]
                                )
                        )
            else:
                wind_series_list.append([])
        else:
            wind_series_list.append([])
        
    case_list_dic['DEMAND_SERIES'] = demand_series_list
    case_list_dic['WIND_SERIES'] = wind_series_list
    case_list_dic['SOLAR_SERIES'] = solar_series_list
                                                
    # Now develop list of component lists
    list_of_component_lists = []
    for case_index in range(num_cases):
        if verbose:
            print 'Preprocess_Input.py:Components for ',case_list_dic['CASE_NAME'][case_index]
        component_list = []
        if 'CAPACITY_COST_NUCLEAR' in have_keys:
            if case_list_dic['CAPACITY_COST_NUCLEAR'][case_index] >= 0:
                component_list.append('NUCLEAR')
                                                
        if 'CAPACITY_COST_NATGAS' in have_keys:
            if case_list_dic['CAPACITY_COST_NATGAS'][case_index] >= 0:
                component_list.append('NATGAS')
                                                
        if 'CAPACITY_COST_WIND' in have_keys:
            if case_list_dic['CAPACITY_COST_WIND'][case_index] >= 0:
                component_list.append('WIND')
                                                
        if 'CAPACITY_COST_NATGAS' in have_keys:
            if case_list_dic['CAPACITY_COST_SOLAR'][case_index] >= 0:
                component_list.append('SOLAR')
                                                
        if 'CAPACITY_COST_STORAGE' in have_keys:
            if case_list_dic['CAPACITY_COST_STORAGE'][case_index] >= 0:
                component_list.append('STORAGE')
                
        if 'DISPATCH_COST_UNMET_DEMAND' in have_keys:
            if case_list_dic['DISPATCH_COST_UNMET_DEMAND'][case_index] >= 0:
                component_list.append('UNMET_DEMAND')
                
        list_of_component_lists.append(component_list)
    case_list_dic['SYSTEM_COMPONENTS'] = list_of_component_lists
    
    #Now case_dic is a dictionary of lists. We want to turn it into a list
    # of dictionaries.  The method for doing this is taken from:
    # https://stackoverflow.com/questions/5558418/list-of-dicts-to-from-dict-of-lists
    
    # case_dic_list = [dict(zip(case_list_dic,t)) for t in zip(*case_list_dic.values())]
    
    # The fancy thing didn't work for me so I will brute force it.
    #
    keywords = case_list_dic.keys()
    case_dic_list = [ {} for  case in range(num_cases)]
    for i in range(num_cases):
        dic = case_dic_list[i]
        for keyword in keywords:
            dic[keyword] = case_list_dic[keyword][i]
        case_dic_list[i] = dic
    
    pickle.dump( [case_list_dic, case_dic_list], open( "test2.pickle", "wb" ) )                           
    return global_dic,case_dic_list

             
