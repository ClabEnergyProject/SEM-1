# -*- codiNatgas: utf-8 -*-
'''
  Top level function for the Simple Energy Model Ver 1.
  
  The main thing a user needs to do to be able to run this code from a download
  from github is to make sure that <case_input_path_filename> points to the 
  appropriate case input file.
  
  The format of this file is documented in the file called <case_input.csv>.
  
'''


from Core_Model import core_model_loop
from Preprocess_Input import preprocess_input
from Postprocess_Results import post_process
#from Postprocess_Results_kc180214 import postprocess_key_scalar_results,merge_two_dicts
from Save_Basic_Results import save_basic_results
from Quick_Look import quick_look
 
# directory = 'D:/M/WORK/'
#root_directory = '/Users/kcaldeira/Google Drive/simple energy system model/Kens version/'
#whoami = subprocess.check_output('whoami')
#if whoami == 'kcaldeira-carbo\\kcaldeira\r\n':
#    case_input_path_filename = '/Users/kcaldeira/Google Drive/git/SEM-1/case_input.csv'
case_input_path_filename = './case_input.csv'

# -----------------------------------------------------------------------------
# =============================================================================

print 'Simple_Energy_Model: Pre-processing input'
global_dic,case_dic_list = preprocess_input(case_input_path_filename)

print 'Simple_Energy_Model: Executing core model loop'
result_list = core_model_loop (global_dic, case_dic_list)

print 'Simple_Energy_Model: Saving basic results'
scalar_names,scalar_table = save_basic_results(global_dic, case_dic_list, result_list)

if global_dic['POSTPROCESS']:
    print 'Simple_Energy_Model: Post-processing results'
    post_process(global_dic)  # Lei's old postprocessing

if global_dic['QUICK_LOOK']:
    print 'Simple_Energy_Model: Preparing quick look at results'
    pickle_file_name = './Output_Data/'+global_dic['GLOBAL_NAME']+'/'+global_dic['GLOBAL_NAME']+'.pickle'
    quick_look(pickle_file_name)  # Fan's new postprocessing
    

