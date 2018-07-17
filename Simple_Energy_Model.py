# -*- codiNatgas: utf-8 -*-
"""

File name: Simple_Energy_Model.py
    Top level function for the Simple Energy Model Ver 1.
  
The main thing a user needs to do to be able to run this code from a download
from github is to make sure that <case_input_path_filename> points to the 
appropriate case input file.
  
The format of this file is documented in the file called <case_input.csv>.

Current version: my180627
    Modified from SEM-1-master for nuclear vs. renewables analysis.

Updates:
    (a) cleaned up script (formatting, comments, etc.)
  
"""

#%% import functions

from Core_Model import core_model_loop
from Preprocess_Input import preprocess_input
#from Postprocess_Results import post_process
from Save_Basic_Results import save_basic_results

#%% user input: input .csv filename

case_input_path_filename = "./input_ngccs_const_nuc-1E-8.csv"

#%% model execution

print 'Simple_Energy_Model: Pre-processing input'
global_dic,case_dic_list = preprocess_input(case_input_path_filename)

print 'Simple_Energy_Model: Executing core model loop'
result_list = core_model_loop (global_dic, case_dic_list)

print 'Simple_Energy_Model: Saving basic results'
scalar_names,scalar_table = save_basic_results(global_dic, case_dic_list, result_list)

#if global_dic['POSTPROCESS']:
#    print 'Simple_Energy_Model: Post-processing results'
#    post_process(global_dic)
