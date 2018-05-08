# -*- codiNatgas: utf-8 -*-
"""
  Top level function for the Simple Energy Model Ver 1.
  
  The main thing a user needs to do to be able to run this code from a download
  from github is to make sure that <case_input_path_filename> points to the 
  appropriate case input file.
  
  The format of this file is documented in the file called <case_input.csv>.
  
"""


from Core_Model import core_model_loop
from Preprocess_Input import preprocess_input
from Postprocess_Results import post_process
#from Postprocess_Results_kc180214 import postprocess_key_scalar_results,merge_two_dicts
from Save_Basic_Results import save_basic_results
import subprocess

#%%

# directory = "D:/M/WORK/"
#root_directory = "/Users/kcaldeira/Google Drive/simple energy system model/Kens version/"
whoami = subprocess.check_output('whoami')
if whoami == 'kcaldeira-carbo\\kcaldeira\r\n':
    case_input_path_filename = "/Users/kcaldeira/Google Drive/git/SEM-1/case_input.csv"

# -----------------------------------------------------------------------------
# =============================================================================

case_dic = preprocess_input(case_input_path_filename)

result_list = core_model_loop (case_dic)

scalar_names,scalar_table = save_basic_results(case_dic, result_list)

if switch_postprocess == True:
    post_process(case_dic, result_list)
