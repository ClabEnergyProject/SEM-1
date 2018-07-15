# -*- coding: utf-8 -*-
"""
Quick_Look.py

Function: this file collects defined functions for plotting optimization results
    from one optimization run or mutilple runs

Functions defined
    func_graphics_dispatch_mix_1scenario()
    func_graphics_dispatch_mix_time_selection_1scenario()
    func_graphics_dispatch_mix_technology_timeseries_1scenario()
    func_graphics_dispatch_var_Nscenarios()
    func_graphics_system_results_Nscenarios()
    func_optimization_results_time_series_1scenario() -- directly callable
    func_optimization_results_system_results_Nscenarios() -- directly callable
    func_optimization_results_dispatch_var_Nscenarios() -- directly callable

History
    Jun 4-5, 2018 completely rewritten
        func_graphics_dispatch_mix_1scenario()
        func_graphics_dispatch_mix_time_selection()
        func_graphics_dispatch_var_Nscenarios()
                        
    Jun 17-18, 2018 added a new function, and updated the comments
        func_graphics_system_results_Nscenarios()

    Jun 19, 2018
        fixed some errors in func_graphics_dispatch_mix_1scenario()
        rewrote some function names
    Jun 20, 2018
        slight changes due to changes the definition of func_lines_2yaxes_plot()
        added the dual y-axes for some figures in func_graphics_system_results_Nscenarios()
        added two functions for multiple-scenario analysis
            func_optimization_results_snapshot_Nscenarios()
            func_optimization_results_dispatch_var_Nscenarios()
    Jun 21, 2018
        fixed errors caused by using the actual division than the integer division.
        added parallel axes for some figures in 
            func_graphics_dispatch_mix_1scenario()
            func_graphics_dispatch_mix_time_selection_1scenario()
            func_graphics_time_series_results_1scenario()
            func_graphics_dispatch_var_Nscenarios()
            func_optimization_results_system_results_Nscenarios()
        changed packaging functions' names
            func_graphics_time_series_results_1scenario -> func_optimization_results_time_series_1scenario
            func_optimization_results_snapshot_Nscenarios -> func_optimization_results_system_results_Nscenarios
        changed the function func_graphics_dispatch_mix_1scenario()
            from fixed ranges in time to dynamically select the weeks with the largest/smallest share of a technology
    Jun 22-23, 2018
        updated the following two functions
            func_optimization_results_system_results_Nscenarios()
            func_graphics_dispatch_mix_time_selection_1scenario()
        .. so that the selected time ranges are determined for the "extreme" weeks
        .. for a technology of interest
    Jun 23, 2018 checked the code and comments
    June 23-24, 2018 updated texts and labels on figures
    Jul 8, 2018 [kc]
        Started making changes so this code runs off of dictionaries rather
        than pickle files. Name changed to <Quick_Look.py>
            
@author: Fan Tong
"""

from __future__ import division  # Allows an integer divided by an integer to return a real.
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pickle
from Supporting_Functions import func_find_period
from Supporting_Functions import func_lines_plot
from Supporting_Functions import func_lines_2yaxes_plot
from Supporting_Functions import func_stack_plot
from Supporting_Functions import func_time_conversion
from Supporting_Functions import func_load_optimization_results
from matplotlib.backends.backend_pdf import PdfPages

#%%
#==============================================================================
# func_graphics_dispatch_mix_1scenario
#
# Purpose
#   Generate dispatch mix figures. Right now, there are N*4 figures.
#       N=3 corresponds to different temporal resolutions: hourly, daily, weekly.
#       4 corresponds to subplots for the same "information" (time scale).
#
# Input
#   A packaging dictionary variable: input_data, which contrains the following data
#       [1] results_matrix_dispatch:  dispatch mix for a particular scenario
#       [2] demand
#   the following texts
#       [3] legend_list
#       [4] title_text
#   and the following controls for graphical outputs
#       [5] SAVE_FIGURES_TO_PDF:   logical variable [0/1]
#       [6] directory_output:      a complete directory, ending with "/"
#       [7] graphics_file_name
#
#   Data dimentions
#       results_matrix_dispatch
#           ROW dimension: optimization time steps
#           COLUMN dimension: technology options (that dispatched energy)
#       demand
#           ROW dimension: optimization time steps
#           Column dimension: none
#       legend list
#           Number of STRING items: technology options (that dispatched energy)
#
# Output
#   6 figures in the console window.
#   You can choose to save them to a PDF book or not.
#
# History
#   Jun 4-5, 2018 started and finished
#   Jun 21, 2018 
#       fixed the bug caused by using the actual division rather than the default floor division.
#       updated the time selection from predefined to dynamically determined.
#
# @Fan Tong
#
#    Jul 9, 2018 Convert to use with the base version of the Simple Energy Model
# @Ken Caldeira
#
#==============================================================================


def quick_look(pickle_file_name):
    
    with open(pickle_file_name, 'rb') as db:
        global_dic,case_dic_list,result_list = pickle.load( db )
        
    verbose = global_dic['VERBOSE']
    if verbose:
        print 'pickle file '+ pickle_file_name+' read'
        
    # --------------- define and open output files -------------------------
    
    output_dir = global_dic['OUTPUT_PATH'] + '/' + global_dic['GLOBAL_NAME']
        # Create the ouput folder    
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Define file for pdfs containing figures comparing cases
    output_all = global_dic['GLOBAL_NAME'] + '_all_cases.pdf'
    pdf_all = PdfPages(output_dir + '/' + output_all) # create and open pdf file
    # Define file for pdfs containing figures relating to individual cases
    output_each = global_dic['GLOBAL_NAME'] + '_each_case.pdf'
    pdf_each = PdfPages(output_dir + '/' + output_each) # create and open pdf file
    # Define file for text output
    output_text = global_dic['GLOBAL_NAME'] + '_text.txt'
    text_file = open(output_dir + '/' + output_text,'w')
        
    # --------------- define colors for plots --------------------- 
    color_DEMAND = "black"
    color_NATGAS  = "tomato" # not explicitly referenced but referenced through eval()
    color_SOLAR   = "wheat" # not explicitly referenced but referenced through eval()
    color_WIND    = "skyblue" # not explicitly referenced but referenced through eval()
    color_NUCLEAR = "limegreen" # not explicitly referenced but referenced through eval()
    color_STORAGE = "orchid"
    color_PGP_STORAGE =  "mediumslateblue"
    color_DISPATCH_CURTAILMENT =  "peru"
    color_UNMET_DEMAND =  "lightslategrey" # not explicitly referenced but referenced through eval()
    
    num_cases = len (case_dic_list) # number of cases
    # 'SYSTEM_COMPONENTS' -- LIST OF COMPONENTS, CHOICES ARE: 'WIND','SOLAR', 'NATGAS','NUCLEAR','STORAGE', 'PGP_STORAGE', 'UNMET'    
    # Loop around and make output for individual cases  
    
    # ============= CREATE LIST OF input_data DICTIONARIES FOR PLOTTING PROGRAMS =========
    
    input_data_list = [] # list of input_data dictionaries
    for case_idx in range(num_cases):
        
        case_dic = case_dic_list[case_idx] # get the input data for case in question
        if verbose:
            print 'preparing case ',case_idx,' ', case_dic['CASE_NAME']
        result_dic = result_list[case_idx] # get the results data for case in question
        input_data = {} # Dictionary of input data for 1scenario graphics fucntion
        input_data["case_name"] = case_dic["CASE_NAME"]
        input_data["demand"] = np.array(case_dic["DEMAND_SERIES"])
        
        input_data['pdf_each'] = pdf_each # file handle for pdf output case by case
        input_data['text_file'] = text_file # file handle for text output case by case
        system_components = case_dic["SYSTEM_COMPONENTS"]
        input_data['system_components'] = system_components

        # results_matrix_dispatch contains time series of things that add electricity to the grid
        # where unmet_demand is considered a pure variable cost source
        
        # Now build the array of dispatch technologies to be plotted for this case
        results_matrix_dispatch = []
        legend_list_dispatch = []
        color_list_dispatch = []
        component_index_dispatch = {}

        for component in system_components:
            addfrom = ''
            if component == 'STORAGE' or component == 'PGP_STORAGE': 
                addfrom = 'FROM_'
            results_matrix_dispatch.append(result_dic['DISPATCH_' + addfrom + component ])
            legend_list_dispatch.append( 'DISPATCH_' + addfrom + component +' kW' )
            color_list_dispatch.append(eval('color_' + component))
            component_index_dispatch[component] = len(results_matrix_dispatch)-1 # row index for each component
        
        input_data["results_matrix_dispatch"] = np.transpose(np.array(results_matrix_dispatch))
        input_data["legend_list_dispatch"] = legend_list_dispatch
        input_data["component_index_dispatch"] = component_index_dispatch
        input_data["color_list_dispatch"] = color_list_dispatch

        # Now build the array of demand components to be plotted for this case
        # NOTE: this should  check that all these options are in the scenario
        # The next set of things gets electricity from the grid
        results_matrix_demand = [case_dic["DEMAND_SERIES"]]
        legend_list_demand = ['demand (kW)]']
        color_list_demand = [color_DEMAND]
        component_index_demand = {'DEMAND':1}
        
        for component in system_components:
            if component == 'STORAGE':
                results_matrix_demand.append(result_dic["DISPATCH_TO_STORAGE"])
                legend_list_demand.append('dispatch to storage (kW)')
                color_list_demand.append(color_STORAGE)
                component_index_demand["STORAGE"] = len(results_matrix_demand)-1
            elif component == 'PGP_STORAGE': 
                results_matrix_demand.append(result_dic["DISPATCH_TO_PGP_STORAGE"])
                legend_list_demand.append('dispatch to pgp storage (kW)')
                color_list_demand.append(color_PGP_STORAGE)
                component_index_demand["PGP_STORAGE"] = len(results_matrix_demand)-1
        
        legend_list_demand.append('curtailment (kW)')
        results_matrix_demand.append(result_dic["DISPATCH_CURTAILMENT"])
        color_list_demand.append(color_DISPATCH_CURTAILMENT)
        component_index_demand["DISPATCH_CURTAILMENT"] = len(results_matrix_demand)-1
        
        input_data["results_matrix_demand"] = np.transpose(np.array(results_matrix_demand))
        input_data["legend_list_demand"] = legend_list_demand
        input_data["component_index_demand"] = component_index_demand
        input_data["color_list_demand"] = color_list_demand
        
        input_data_list.append(input_data)
    if verbose:
        print 'input_data dictionaries created for plotting programs'
        
        # end of section to generate list of input_data dictionaries

    # ========== CREATE PLOTS =========
  
    for input_data in input_data_list:
        func_optimization_results_time_series_1scenario (input_data) # produce single case plots
        if verbose:
            print 'func_optimization_results_time_series_1scenario executed'
            
            
    # ============= LOGIC FOR COMPARING CASES ==============================
    
    
#        func_optimization_results_system_results_Nscenarios (input_data) # produce weeks of the most extreme values
#        if verbose:
#            print 'func_optimization_results_system_results_Nscenarios executed'
#        func_optimization_results_dispatch_var_Nscenarios (input_data)
#        if verbose:
#            print 'func_optimization_results_dispatch_var_Nscenarios executed'
#    func_optimization_results_time_series_1scenario() -- directly callable
#    func_optimization_results_system_results_Nscenarios() -- directly callable
#    func_optimization_results_dispatch_var_Nscenarios() -- directly callable
         
    # close files
    pdf_all.close()
    pdf_each.close()
    text_file.close()
    if verbose:
        print 'files closed'

       
def func_graphics_dispatch_mix_1scenario (input_data):    
    
    # -------------------------------------------------------------------------
    # Get the input data
    
    demand = input_data["demand"]
    results_matrix_dispatch = input_data["results_matrix_dispatch"]
    results_matrix_demand = input_data["results_matrix_demand"]
    pdf_each = input_data["pdf_each"]
    legend_list_dispatch = input_data["legend_list_dispatch"]
    legend_list_demand = input_data["legend_list_demand"]
    case_name = input_data["case_name"]
    
    # -------------------------------------------------------------------------    
    # -------------------------------------------------------------------------
    # Define the plotting style
    
    plt.style.use('default')
    # plt.style.use('bmh')
    # plt.style.use('fivethirtyeight')
    # plt.style.use('seaborn-white')
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] =  'Helvetica ' #'Palatino' # 'Ubuntu'
    plt.rcParams['font.monospace'] = 'Helvetica Mono' #'Palatino Mono' # 'Ubuntu'
    plt.rcParams['font.size'] = 16
    plt.rcParams['axes.labelsize'] = 16
    plt.rcParams['axes.labelweight'] = 'bold'
    plt.rcParams['axes.titlesize'] = 16
    plt.rcParams['xtick.labelsize'] = 16
    plt.rcParams['ytick.labelsize'] = 16
    plt.rcParams['legend.fontsize'] = 14
    plt.rcParams['figure.titlesize'] = 16
    plt.rcParams['lines.linewidth'] = 2.0
    plt.rcParams['grid.color'] = 'k'
    plt.rcParams['grid.linestyle'] = ':'
    plt.rcParams['grid.linewidth'] = 0.5
    plt.rcParams['xtick.major.width'] = 2
    plt.rcParams['xtick.major.size'] = 6
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.major.width'] = 2
    plt.rcParams['ytick.major.size'] = 6
    plt.rcParams['ytick.direction'] = 'in'
    
    figsize_oneplot = (8,6)
    
    # -------------------------------------------------------------------------
    # Figures 1 Hourly time series results
    
    # Four figures: 2 (dispatch, demand) * 2 (line plots, stack plots)
    
    # -------------
    
    
    optimization_time_steps = demand.size
    x_data = np.arange(0, optimization_time_steps)
    
    # -------------
    
    figure1a = plt.figure(figsize=figsize_oneplot)
    ax1a = figure1a.add_subplot(221)
    
    inputs_dispatch = {
        "x_data":           x_data, 
#        "y_data":           results_matrix_dispatch,
        "y_data":           results_matrix_dispatch,
#        'z_data':           demand,
        'z_data':           demand,
        "ax":               ax1a,
        "x_label":          'Time (hour in the year)',
        "y_label":          'kW',
        "title":            case_name +': Dispatch mix',
        "legend":           legend_list_dispatch,
        "legend_z":         'demand',
        "line_width":       2,
        "line_width_z":     0.2,
        'grid_option':      0,
        }        

    func_lines_plot(inputs_dispatch)
    
    # -------------
    
    #figure1b = plt.figure(figsize=figsize_oneplot)
    ax1b = figure1a.add_subplot(222)

    inputs_dispatch["ax"] = ax1b
    func_stack_plot(inputs_dispatch)
    
    # -------------

    #figure1c = plt.figure(figsize=figsize_oneplot)
    ax1c = figure1a.add_subplot(223)

    inputs_demand = {
        "x_data":           x_data, 
        "y_data":           results_matrix_demand,
        #'z_data':           demand,
        "ax":               ax1c,
        "x_label":          'Time (hour in the year)',
#        "y_label":          'kW',
        "title":            case_name+': Demand mix',
        "legend":           legend_list_demand,
        #"legend_z":         'demand',
        "line_width":       2,
        #"line_width_z":     0.2,
        'grid_option':      0,
        } 
          
    func_lines_plot(inputs_demand)
    
    # -------------
    
    #figure1d = plt.figure(figsize=figsize_oneplot)
    ax1d = figure1a.add_subplot(224)

    inputs_demand["ax"] = ax1d
    
    func_stack_plot(inputs_demand) 

    # -------------

    pdf_each.savefig(figure1a, bbox_inches='tight')
    #plt.close()
    
    #pdf_each.savefig(figure1b, bbox_inches='tight')
    #plt.close()
    
    #pdf_each.savefig(figure1c, bbox_inches='tight')
    #plt.close()
    
    #pdf_each.savefig(figure1d, bbox_inches='tight')
    plt.close()
        
    # -------------------------------------------------------------------------
    
    # Figures 2 Daily results
    
    # Four figures: 2 (dispatch, demand) * 2 (line plots, stack plots)

    # -------------

    temporal_scale = 24
    x_data = np.arange(0, optimization_time_steps/temporal_scale)
    
    results_matrix_dispatch2 = np.zeros(
        (int(results_matrix_dispatch.shape[0]/temporal_scale), 
        int(results_matrix_dispatch.shape[1])))

    for i in xrange(results_matrix_dispatch2.shape[1]):
        results_matrix_dispatch2 [:,i] = \
            func_time_conversion(results_matrix_dispatch[:,i],temporal_scale)

    results_matrix_demand2 = np.zeros(
        (int(results_matrix_demand.shape[0]/temporal_scale), 
        int(results_matrix_demand.shape[1])))
    
    for i in xrange(results_matrix_demand2.shape[1]):
        results_matrix_demand2 [:,i] = \
            func_time_conversion(results_matrix_demand[:,i],temporal_scale)

    # -------------

    figure2a = plt.figure(figsize=figsize_oneplot)
    ax2a = figure2a.add_subplot(2,2,1)

    inputs_dispatch = {
        "x_data":           x_data, 
        "y_data":           results_matrix_dispatch2,
        "z_data":           func_time_conversion(demand,temporal_scale),
        "z2_data":           func_time_conversion(demand/np.average(demand),temporal_scale),
        "ax":               ax2a,
        "x_label":          'Time (day in the year)',
        "y_label":          'kW',
        "title":            case_name+': Dispatch mix',
        "legend":           legend_list_dispatch,
        "legend_z":         'demand',
        "line_width":       2,
        "line_width_z":     1,
        'grid_option':      0,
        }
    
    func_lines_plot(inputs_dispatch)
    
    # -------------
    
    #figure2b = plt.figure(figsize=figsize_oneplot)
    ax2b = figure2a.add_subplot(2,2,2)
    inputs_dispatch['ax'] = ax2b
    
    func_stack_plot(inputs_dispatch)

    # -------------

    #figure2c = plt.figure(figsize=figsize_oneplot)
    ax2c = figure2a.add_subplot(2,2,3)

    # -------------

    inputs_demand = {
        "x_data":           x_data, 
        "y_data":           results_matrix_demand2,
        #"z_data":           func_time_conversion(demand,temporal_scale),
        "ax":               ax2c,
        "x_label":          'Time (day in the year)',
        "y_label":          'kW',
        "title":            case_name+': Demand mix',
        "legend":           legend_list_demand,
        #"legend_z":         'demand',
        "line_width":       2,
        #"line_width_z":     1,
        'grid_option':      0,
        }

    func_lines_plot(inputs_demand)
    
    # -------------

    #figure2d = plt.figure(figsize=figsize_oneplot)
    ax2d = figure2a.add_subplot(2,2,4)
    inputs_demand['ax'] = ax2d
    
    func_stack_plot(inputs_demand) 
    
    # -------------
    
    pdf_each.savefig(figure2a, bbox_inches='tight')
    #plt.close()
    
    #pdf_each.savefig(figure2b, bbox_inches='tight')
    #plt.close()
    
    #pdf_each.savefig(figure2c, bbox_inches='tight')
    #plt.close()
    
    #pdf_each.savefig(figure2d, bbox_inches='tight')
    plt.close()

    # -------------------------------------------------------------------------
    # Figures 3 Weekly time series results

    # Four figures: 2 (dispatch, demand) * 2 (line plots, stack plots)

    # -------------

    temporal_scale = 24 * 7
    x_data = np.arange(0, np.floor (optimization_time_steps/temporal_scale))
    
    # --------------------
    
    # Note: 
    #   (1) use floor_division to be compatiable with func_time_conversion()    
    #   (2) force type conversion to integer for slice indices
    
    results_matrix_dispatch3 = np.zeros(
        (int(np.floor(results_matrix_dispatch.shape[0]/temporal_scale)), 
        int(results_matrix_dispatch.shape[1]))
        )

    for i in xrange(results_matrix_dispatch3.shape[1]):
        results_matrix_dispatch3 [:,i] = \
            func_time_conversion(results_matrix_dispatch[:,i],temporal_scale)

    results_matrix_demand3 = np.zeros(
        (int(np.floor(results_matrix_demand.shape[0]/temporal_scale)),
        int(results_matrix_demand.shape[1]))
        )
    
    for i in xrange(results_matrix_demand3.shape[1]):
        results_matrix_demand3 [:,i] = \
            func_time_conversion(results_matrix_demand[:,i],temporal_scale)
    
    # --------------------

    figure3a = plt.figure(figsize=figsize_oneplot)
    ax3a = figure3a.add_subplot(2,2,1)

    inputs_dispatch = {
        "x_data":           x_data, 
        "y_data":           results_matrix_dispatch3,
        "z_data":           func_time_conversion(demand,temporal_scale),
        "z2_data":          func_time_conversion(demand/np.average(demand),temporal_scale),
        "ax":               ax3a,
        "x_label":          'Time (week in the year)',
        "y_label":          'kW',
        "title":            case_name+': Dispatch mix',
        "legend":           legend_list_dispatch,
        "legend_z":         'demand',
        "line_width":       2,
        "line_width_z":     1,
        'grid_option':      0,
        }

    func_lines_plot(inputs_dispatch)
    
    # --------------------
    
    #figure3b = plt.figure(figsize=figsize_oneplot)
    ax3b = figure3a.add_subplot(2,2,2)
    inputs_dispatch['ax'] = ax3b
    
    func_stack_plot(inputs_dispatch)

    # --------------------
    
    #figure3c = plt.figure(figsize=figsize_oneplot)
    ax3c = figure3a.add_subplot(2,2,3)
    
    inputs_demand = {
        "x_data":           x_data, 
        "y_data":           results_matrix_demand3,
        #"z_data":           func_time_conversion(demand,temporal_scale),
        "ax":               ax3c,
        "x_label":          'Time (week in the year)',
        "y_label":          'kW',
        "title":            case_name+': Demand mix',
        "legend":           legend_list_demand,
        #"legend_z":         'demand',
        "line_width":       2,
        #"line_width_z":     1,
        'grid_option':      0,
        }

    func_lines_plot(inputs_demand)
    
    # --------------------
    
    #figure3d = plt.figure(figsize=figsize_oneplot)
    ax3d = figure3a.add_subplot(2,2,4)
    inputs_demand['ax'] = ax3d
    
    func_stack_plot(inputs_demand)
    
    # --------------------
    
    pdf_each.savefig(figure3a, bbox_inches='tight')
    #plt.close()
    
    #pdf_each.savefig(figure3b, bbox_inches='tight')
    #plt.close()
    
    #pdf_each.savefig(figure3c, bbox_inches='tight')
    #plt.close()
    
    #pdf_each.savefig(figure3d, bbox_inches='tight')
    plt.close()
    
    # -------------------------------------------------------------------------


#==============================================================================
# func_graphics_dispatch_mix_time_selection_1scenario
#
# Purpose
#   Generate two time series figures (line plots and stack plots) 
#       for a mix of technologies (dispatch mix) or a mix of demands (demand mix)
#
# Input
#   A packaging dictionary variable: input_data, which contrains the following data
#       [1] mix_matrix:  dispatch mix or demand mix
#       [2] demand:      demand data
#       [3] time_range:  the time period of interest
#   the following texts
#       [3] legend_list
#       [4] title_text
#   and the following controls for graphical outputs
#       [5] SAVE_FIGURES_TO_PDF:   logical variable [0/1]
#       [6] pdf_each:   a <PDF> object passed from the outer function
#        
#   Data dimentions
#       mix_matrix
#           ROW dimension: optimization time steps
#           COLUMN dimension: technology options or types of demands
#       demand
#           ROW dimension: optimization time steps
#           Column dimension: none
#       legend list
#           list of STRINGs: correspond to the COLUMN of mix_matrix
#
# Output
#   Generate 2 figures (line plots and stack plots)
#   The outer function will determine the file saving option.
#
# Usage
#   Show dispatch mix time series figures for a selective time period.        
#
# History
#   June 4-5, 2018 started and finished the code
#   June 22, 2018 moved (the PDF file creation and closure) to the upper function
#   June 23-24, 2018 updated texts and labels on figures        
#
# @Fan Tong
#==============================================================================

def func_graphics_dispatch_mix_time_selection_1scenario (input_data):
    
    # -------------------------------------------------------------------------
    # Get the input data
    
    demand = input_data["demand"]
    mix_matrix = input_data["mix_matrix"]
    time_range = input_data["time_range"]
    
    legend_list = input_data["legend_list"]
    title_text = input_data["title_text"]
    
    # -------------------------------------------------------------------------
    
    figsize_oneplot = (8, 6)
    
    # -------------------------------------------------------------------------
    # Figures 1-2 Hourly time series results
    
    optimization_time_steps = mix_matrix.shape[0]
    x_data = np.arange(0, optimization_time_steps)    

    # -------------------------------------------------------------------------

    figure1 = plt.figure(figsize=figsize_oneplot)
    ax1 = figure1.add_subplot(111)

    input_data_1 = {
        "x_data_range":     time_range,
        "x_data":           x_data, 
        "y_data":           mix_matrix,
        "ax":               ax1,
        "x_label":          'Time (hour in the year)',
        "y_label":          'kW',
        "title":            title_text,
        "legend":           legend_list,
        "line_width":       2,
        'grid_option':      0,
        }
    func_lines_plot(input_data_1)
    
    # -------------------------
    
    figure2 = plt.figure(figsize=figsize_oneplot)
    ax2 = figure2.add_subplot(111)
    
    input_data_2 = {
        "x_data_range":     time_range,
        "x_data":           x_data, 
        "y_data":           mix_matrix,
        "ax":               ax2,
        "x_label":          'Time (hour in the year)',
        "y_label":          'kW',
        "title":            title_text,
        "legend":           legend_list,
        "line_width":       2,
        'grid_option':      0,
        }
    
    if "demand_line_for_dispatch_figure" in input_data.keys():       
        
        # line_width_z = 1/np.log(optimization_time_steps)*np.log(6)
        
        if (time_range[1] - time_range[0]) < 200:
            line_width_z = 2
        elif (time_range[1] - time_range[0]) < 1000:
            line_width_z = 1.5
        else:
            line_width_z = 1
        
        input_data_2['z_data'] = demand
        input_data_2['z2_data'] = demand/np.average(demand)
        input_data_2['legend_z'] = 'demand'
        input_data_2['line_width_z'] = line_width_z   

    func_stack_plot(input_data_2)    

    # -------------------------

    pdf_each = input_data["pdf_each"]
    
    pdf_each.savefig(figure1, bbox_inches='tight')
    #plt.close()
    
    pdf_each.savefig(figure2, bbox_inches='tight')
    plt.close()
   
#%%
#==============================================================================
# func_graphics_dispatch_var_Nscenarios
#
# Purpose
#   Generate 4*2 figures regarding dispatched energy from a particular technology
#       over a number of scenarios considered.
#   In each pair of figures, different axes are assumed.
#
# Input
#   A packaging dictionary variable: input_data, which contrains the following data
#       [1] results_matrix_dispatch:  
#           dispatch energy time series for the same technology
#           across a number of different scenarios
#       [2] demand
#   the following texts
#       [3] legend_list
#       [4] title_text
#   and the following controls for graphical outputs
#       [5] SAVE_FIGURES_TO_PDF:   logical variable [0/1]
#       [6] directory_output:      a complete directory, ending with "/"
#       [7] graphics_file_name        
#
#   Data dimentions
#       results_matrix_dispatch
#           ROW dimension: optimization time steps
#           COLUMN dimension: different scenarios
#       legend list
#           number of STRING items: different scenarios
#
# Output
#   4 figures in the console window.
#   You can choose to save them to a PDF book or not.
#
# History
#   June 4-5, 2018 started and finished the code
#   June 20, 2018 added "demand" input for axis labels
#   June 24, 2018 added parallel axes, thus reducing the total number of figures to 4
#        
# @Fan Tong
#==============================================================================

def func_graphics_dispatch_var_Nscenarios (input_data):

    # -------------------------------------------------------------------------
    # Get the input data
    
    pdf_all = input_data['pdf_all']
    demand = input_data["demand"]
    results_matrix_dispatch = input_data["results_matrix_dispatch"]
    
    legend_list = input_data["legend_list"]
    title_text = input_data["title_text"]   
    
    
    # -------------------------------------------------------------------------
    # Define the plotting style
    
    plt.style.use('default')
    # plt.style.use('bmh')
    # plt.style.use('fivethirtyeight')
    # plt.style.use('seaborn-white')
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] =  'Helvetica ' #'Palatino' # 'Ubuntu'
    plt.rcParams['font.monospace'] = 'Helvetica Mono' #'Palatino Mono' # 'Ubuntu'
    plt.rcParams['font.size'] = 16
    plt.rcParams['axes.labelsize'] = 16
    plt.rcParams['axes.labelweight'] = 'bold'
    plt.rcParams['axes.titlesize'] = 16
    plt.rcParams['xtick.labelsize'] = 16
    plt.rcParams['ytick.labelsize'] = 16
    plt.rcParams['legend.fontsize'] = 14
    plt.rcParams['figure.titlesize'] = 16
    plt.rcParams['lines.linewidth'] = 2.0
    plt.rcParams['grid.color'] = 'k'
    plt.rcParams['grid.linestyle'] = ':'
    plt.rcParams['grid.linewidth'] = 0.5
    plt.rcParams['xtick.major.width'] = 2
    plt.rcParams['xtick.major.size'] = 6
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.major.width'] = 2
    plt.rcParams['ytick.major.size'] = 6
    plt.rcParams['ytick.direction'] = 'in'
    
    # -------------------------------------------------------------------------
    
    figsize_oneplot = (8,6)
    
    # -------------------------------------------------------------------------
    
    # Figure 1 Sorted time series of discharging - y axis option #1
    
    # -----------------------------
    
    optimization_time_steps = results_matrix_dispatch.shape[0]
    x_data = np.arange(0, optimization_time_steps)
    
    results_matrix_dispatch1 = np.zeros(
            results_matrix_dispatch.shape)
    
    for i in xrange(results_matrix_dispatch.shape[1]):
        results_matrix_dispatch1 [:,i] = \
            -np.sort(-np.reshape(results_matrix_dispatch[:,i], -1))
    
    # -----------------------------
    
    figure1 = plt.figure(figsize=figsize_oneplot)
    ax1 = figure1.add_subplot(111)
    
    inputs = {
            "x_data":       x_data, 
            "y_data":       results_matrix_dispatch1,
            "ax":           ax1,
            "x_label":      'Time (hour in the year)',
            "y_label":      'kW',
            "title":        title_text,
            "legend":       legend_list,
            "line_width":    2,
            'grid_option':   1,
            }        
            
    func_lines_plot(inputs)
    
    pdf_all.savefig(figure1, bbox_inches='tight')
        
#    # ---------------------------
#    
#    # Figure 1b  Sorted time series of discharging - y axis option #2
#    
#    # -----------------------------
#    
##    optimization_time_steps = results_matrix_dispatch.shape[0]
##    x_data = np.arange(0, optimization_time_steps)
##    
##    results_matrix_dispatch1 = np.zeros(
##            results_matrix_dispatch.shape)
##    
##    for i in xrange(results_matrix_dispatch.shape[1]):
##        results_matrix_dispatch1 [:,i] = \
##            -np.sort(-np.reshape(results_matrix_dispatch[:,i], -1))
#    
#    # -----------------------------
#    
#    figure1b = plt.figure(figsize=figsize_oneplot)
#    ax1b = figure1b.add_subplot(111)
#    
#    inputs = {
#            "x_data":       x_data, 
#            "y_data":       results_matrix_dispatch1/np.average(demand),
#            "ax":           ax1b,
#            "x_label":      'Time (hour in the year)',
#            "y_label":      'Dispatched energy\n(hourly-average demand)',
#            "title":        title_text,
#            "legend":       legend_list,
#            "line_width":    2,
#            'grid_option':   1,
#            }        
#            
#    func_lines_plot(inputs)
#    
#    if SAVE_FIGURES_TO_PDF:
#        pdf_each.savefig(figure1b, bbox_inches='tight')
#        plt.close()
        
    # -------------------------------------------------------------------------
    # Figure 2. Time series of discharging - y axis option #1
    
    # -----------------------------
    
    # x_data = np.arange(0, optimization_time_steps)
    
    # -----------------------------
    
    figure2 = plt.figure(figsize=figsize_oneplot)
    ax2 = figure2.add_subplot(111)
    
    inputs = {
            "x_data":       x_data, 
            "y_data":       results_matrix_dispatch,
            "ax":           ax2,
            "x_label":      'Time (hour in the year)',
            "y_label":      'kW',
            "title":        title_text,
            "legend":       legend_list,
            "line_width":    1,
            'grid_option':   0,
            }
    
    func_lines_plot(inputs)
    
    pdf_all.savefig(figure2, bbox_inches='tight')
    #plt.close()
    
#    # -------------------------
#    
#    #%% Figure 2b Time series of discharging - y axis option #2
#    
#    # -------------------------
#    
##    x_data = np.arange(0, optimization_time_steps)
#    
#    # -------------------------
#    
#    figure2b = plt.figure(figsize=figsize_oneplot)
#    ax2b = figure2b.add_subplot(111)
#    
#    inputs = {
#            "x_data":       x_data, 
#            "y_data":       results_matrix_dispatch/np.average(demand),
#            "ax":           ax2b,
#            "x_label":      'Time (hour in the year)',
#            "y_label":      'Discharged energy\n(hourly-average demand)',
#            "title":        title_text,
#            "legend":       legend_list,
#            "line_width":    1,
#            'grid_option':   0,
#            }
#    
#    func_lines_plot(inputs)
#    
#    if SAVE_FIGURES_TO_PDF:
#        pdf_each.savefig(figure2b, bbox_inches='tight') 
#        plt.close()
    
    # -------------------------------------------------------------------------
    # Figure 3 Time series of discharging - downscale to daily - y axis option #1
    
    # -------------------------
    
    temporal_scale = 24
    x_data = np.arange(0, optimization_time_steps/temporal_scale)
    
    results_matrix_dispatch1 = np.zeros(
            (int(results_matrix_dispatch.shape[0]/temporal_scale), 
            int(results_matrix_dispatch.shape[1])))
    
    for i in xrange(results_matrix_dispatch.shape[1]):
        results_matrix_dispatch1 [:,i] = \
            func_time_conversion(results_matrix_dispatch[:,i],temporal_scale)
    
    # -------------------------
    
    figure3 = plt.figure(figsize=figsize_oneplot)
    ax3 = figure3.add_subplot(111)
    
    inputs = {
            "x_data":       x_data, 
            "y_data":       results_matrix_dispatch1,
            "ax":           ax3,
            "x_label":      'Time (day in the year)',
            "y_label":      'kW',
            "title":        title_text,
            "legend":       legend_list,
            "line_width":    1,
            'grid_option':   0,
            }        
            
    func_lines_plot(inputs)
    
    pdf_all.savefig(figure3, bbox_inches='tight')
    #plt.close()
    
#    # ---------------------------
#    # Figure 3b. Time series of discharging - downscale to daily - y axis option #2
#    
#    # -------------------------
#    
##    temporal_scale = 24
##    x_data = np.arange(0, optimization_time_steps/temporal_scale)
##    
##    results_matrix_dispatch1 = np.zeros(
##            (int(results_matrix_dispatch.shape[0]/temporal_scale), 
##            int(results_matrix_dispatch.shape[1])))
##    
##    for i in xrange(results_matrix_dispatch.shape[1]):
##        results_matrix_dispatch1 [:,i] = \
##            func_time_conversion(results_matrix_dispatch[:,i],temporal_scale)
#    
#    # -------------------------
#    
#    figure3b = plt.figure(figsize=figsize_oneplot)
#    ax3b = figure3b.add_subplot(111)
#    
#    inputs = {
#            "x_data":       x_data, 
#            "y_data":       results_matrix_dispatch1/np.average(demand),
#            "ax":           ax3b,
#            "x_label":      'Time (day in the year)',
#            "y_label":      'Discharged energy\n(hourly-average demand)',
#            "title":        title_text,
#            "legend":       legend_list,
#            "line_width":    1,
#            'grid_option':   0,
#            }        
#            
#    func_lines_plot(inputs)
#    
#    if SAVE_FIGURES_TO_PDF:
#        pdf_each.savefig(figure3b, bbox_inches='tight')  
#        plt.close()
    
    # -----------------------------------------------------------------------------
    
    # Figure 4 Time series of discharging - downscale to weekly - y axis option #1
    
    # -------------------------
    
    temporal_scale = 24 * 7
    x_data = np.arange(0, int(np.floor(optimization_time_steps/temporal_scale)))
    
    results_matrix_dispatch1 = np.zeros(
            (int(np.floor(results_matrix_dispatch.shape[0]/temporal_scale)), 
            int(results_matrix_dispatch.shape[1])))
    
    for i in xrange(results_matrix_dispatch.shape[1]):
        results_matrix_dispatch1 [:,i] = \
            func_time_conversion(results_matrix_dispatch[:,i],temporal_scale)
    
    # -------------------------
    
    figure4 = plt.figure(figsize=figsize_oneplot)
    ax4 = figure4.add_subplot(111)
    
    inputs = {
            "x_data":       x_data, 
            "y_data":       results_matrix_dispatch1,
            "ax":           ax4,
            "x_label":      'Time (week in the year)',
            "y_label":      'kW',
            "title":        title_text,
            "legend":       legend_list,
            "line_width":    1,
            'grid_option':   0,
            }        
            
    func_lines_plot(inputs)
    
    pdf_all.savefig(figure4, bbox_inches='tight')
    #plt.close()

#    # -----------------------------------------------------------------------------
#    # Figure 4b Time series of discharging - downscale to weekly - y axis option #2
#    
#    # -------------------------
#    
##    temporal_scale = 24 * 7
##    x_data = np.arange(0, optimization_time_steps/temporal_scale)
##    
##    results_matrix_dispatch1 = np.zeros(
##            (int(results_matrix_dispatch.shape[0]/temporal_scale), 
##            int(results_matrix_dispatch.shape[1])))
##    
##    for i in xrange(results_matrix_dispatch.shape[1]):
##        results_matrix_dispatch1 [:,i] = \
##            func_time_conversion(results_matrix_dispatch[:,i],temporal_scale)
#    
#    figure4b = plt.figure(figsize=figsize_oneplot)
#    ax4b = figure4b.add_subplot(111)
#    
#    inputs = {
#            "x_data":       x_data, 
#            "y_data":       results_matrix_dispatch1/np.average(demand),
#            "ax":           ax4b,
#            "x_label":      'Time (week in the year)',
#            "y_label":      'Discharged energy\n(hourly-average demand)',
#            "title":        title_text,
#            "legend":       legend_list,
#            "line_width":    1,
#            'grid_option':   0,
#            }        
#            
#    func_lines_plot(inputs)
#    
#    if SAVE_FIGURES_TO_PDF:
#        pdf_each.savefig(figure4b, bbox_inches='tight')
#        plt.close()
    

#%%
#==============================================================================
# func_graphics_system_results_Nscenarios
#
# Purpose
#   Generate 8 figures regarding the "most interested" system-level results for
#       a series of similar optimizations.        
#
# Input
#   A packaging dictionary variable: input_data, which contrains the following data
#       First, inputs for the optimization model   
#       [1] component_index_dispatch:
#       [2] demand
#       [3] assumptions_matrix
#       Second, results from the optimization model    
#       [4] storage_dispatch_matrix
#       [5] storage_capacity_matrix
#       [6] storage_cycle_matrix
#       [7] storage_investment_matrix
#       [8] power_capacity_matrix
#       [9] power_dispatch_matrix
#       [10] cost_power_matrix
#       [11] cost_everything_matrix
#   and the following controls for graphical outputs
#       [12] x_label          
#       [13] SAVE_FIGURES_TO_PDF:   logical variable [0/1]
#       [14] directory_output:      a complete directory, ending with "/"
#       [15] graphics_file_name       
#
#   Data dimentions
#       assumptions_matrix <np.array> different scenarios
#       storage_***_matrix <np.array> "values" for different scenarios        
#       "_matrix" <np.ndarray>
#           ROW dimension: technology options
#           COLUMN dimension: "values" for different scenarios
#
# Output
#   8 figures in the console window.
#   You can choose to save them to a PDF book or not.
#
# History
#   June 17-18, 2018 started and finished the function
#   June 20, 2018 added parallel axes
#   June 22, 2018 added comments
#        
# @Fan Tong
#==============================================================================
        
def func_graphics_system_results_Nscenarios (input_data):

    # -------------------------------------------------------------------------
    # load the input data
        
    # supporting data
    
    component_index_dispatch = input_data["component_index_dispatch"]
    demand = input_data["demand"]
    
    # core data
    
    assumptions_matrix = input_data["assumptions_matrix"]
    storage_dispatch_matrix = input_data["storage_dispatch_matrix"]
    storage_capacity_matrix = input_data["storage_capacity_matrix"]
    storage_cycle_matrix = input_data["storage_cycle_matrix"]
    storage_investment_matrix = input_data["storage_investment_matrix"]
    power_capacity_matrix = input_data["power_capacity_matrix"]
    power_dispatch_matrix = input_data["power_dispatch_matrix"]
    cost_power_matrix = input_data["cost_power_matrix"]
    cost_everything_matrix = input_data["cost_everything_matrix"]
    
    # graphics-related
    
    x_label = input_data["x_label"]
    pdf_all = input_data["pdf_all"]  # handle for graphics file output for all cases
    
    # -------------------------------------------------------------------------
    
    # Create the output folder
    
    
    # Define the plotting style
    
    plt.style.use('default')
    # plt.style.use('bmh')
    # plt.style.use('fivethirtyeight')
    # plt.style.use('seaborn-white')
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] =  'Helvetica ' #'Palatino' # 'Ubuntu'
    plt.rcParams['font.monospace'] = 'Helvetica Mono' #'Palatino Mono' # 'Ubuntu'
    plt.rcParams['font.size'] = 16
    plt.rcParams['axes.labelsize'] = 16
    plt.rcParams['axes.labelweight'] = 'bold'
    plt.rcParams['axes.titlesize'] = 16
    plt.rcParams['xtick.labelsize'] = 16
    plt.rcParams['ytick.labelsize'] = 16
    plt.rcParams['legend.fontsize'] = 14
    plt.rcParams['figure.titlesize'] = 16
    plt.rcParams['lines.linewidth'] = 2.0
    plt.rcParams['grid.color'] = 'k'
    plt.rcParams['grid.linestyle'] = ':'
    plt.rcParams['grid.linewidth'] = 0.5
    plt.rcParams['xtick.major.width'] = 2
    plt.rcParams['xtick.major.size'] = 6
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.major.width'] = 2
    plt.rcParams['ytick.major.size'] = 6
    plt.rcParams['ytick.direction'] = 'in'
      
    # -------------------------------------------------------------------------
    
    figsize_oneplot = (8,6)
    
    # -------------------------------------------------------------------------
    
    # Figure 1 Storage discharge energy
    
    figure1 = plt.figure(figsize=figsize_oneplot)
    ax1 = figure1.add_subplot(111)
    
    inputs_dispatch_1 = {
        "x_data":           assumptions_matrix, 
        "y_data":          storage_dispatch_matrix ,
        "ax":               ax1,
        "x_label":          x_label,
        "y_label":         'Storage discharge (kW)',
        "line_width":       2,
        "grid_option":      0,
        }
    
    [ax1, ax1b] = func_lines_2yaxes_plot(inputs_dispatch_1)
    
    ax1.set_xscale("log", nonposx='clip')
    ax1.set_yscale("log", nonposx='clip')
    ax1b.set_yscale("log", nonposx='clip')
    
    pdf_all.savefig(figure1, bbox_inches='tight')
    #plt.close()
    
    # -------------------------------------------------------------------------
    
    # Figure 2 Storage capacity
    
    figure2 = plt.figure(figsize=figsize_oneplot)
    ax2 = figure2.add_subplot(111)
    
    inputs_dispatch_2 = {
        "x_data":           assumptions_matrix, 
        "y_data":          storage_capacity_matrix ,
        "ax":               ax2,
        "x_label":          x_label,
        "y_label":         'Storage capacity (kWh)',
        "line_width":       2,
        'grid_option':      0,
        }
    
    [ax2, ax2b] = func_lines_2yaxes_plot(inputs_dispatch_2)
    
    ax2.set_xscale("log", nonposx='clip')
    ax2.set_yscale("log", nonposx='clip')
    ax2b.set_yscale("log", nonposx='clip')
    
    pdf_all.savefig(figure2, bbox_inches='tight')
    #plt.close()
    
    # -------------------------------------------------------------------------
    
    # Figure 3 Full-discharge cycles
    
    figure3 = plt.figure(figsize=figsize_oneplot)
    ax3 = figure3.add_subplot(111)
    
    inputs_dispatch_3 = {
        "x_data":           assumptions_matrix, 
        "y_data":           storage_cycle_matrix,
        "ax":               ax3,
        "x_label":          x_label,
        "y_label":          'Calculated full-discharge cycles',
        "line_width":       2,
        'grid_option':      0,
        }        
    
    ax3.set_xscale("log", nonposx='clip')
    ax3.set_yscale("log", nonposx='clip')
    
    func_lines_plot(inputs_dispatch_3)
    
    pdf_all.savefig(figure3, bbox_inches='tight')
    #plt.close()
    
    # -------------------------------------------------------------------------
    
    # Figure 4 Storage investment
    
    figure4 = plt.figure(figsize=figsize_oneplot)
    ax4 = figure4.add_subplot(111)
    
    inputs_dispatch_4 = {
        "x_data":           assumptions_matrix, 
        "y_data":           storage_investment_matrix ,
        "ax":               ax4,
        "x_label":          x_label,
        "y_label":          'Energy storage investment (billion $)',
        "line_width":       2,
        'grid_option':      0,
        }        
    
    ax4.set_xscale("log", nonposx='clip')
    # ax4.set_yscale("log", nonposx='clip')
    
    func_lines_plot(inputs_dispatch_4)
    
    pdf_all.savefig(figure4, bbox_inches='tight')
    #plt.close()
    
    # -------------------------------------------------------------------------
    
    # Figure 5 Power generation capacity
    
    legend_list = sorted(component_index_dispatch.keys(), key=lambda x: x[1])
    
    figure5 = plt.figure(figsize=figsize_oneplot)
    ax5 = figure5.add_subplot(111)
    
    inputs_dispatch_5 = {
            "x_data":       assumptions_matrix, 
            "y_data":       power_capacity_matrix.T,
            "ax":           ax5,
            "x_label":      'Time (hour in the year)',
            "y_label":      'Power generation capacity (GW)',
            "legend":       legend_list,
            "line_width":    2,
            'grid_option':   0,
            }        
            
    ax5.set_xscale("log", nonposx='clip')
    
    func_stack_plot(inputs_dispatch_5)
    
    pdf_all.savefig(figure5, bbox_inches='tight')
    #plt.close()
    
    # -------------------------------------------------------------------------
    
    # Figure 6 Power generation dispatch mix
    
    legend_list = sorted(component_index_dispatch.keys(), key=lambda x: x[1])
    
    figure6 = plt.figure(figsize=figsize_oneplot)
    ax6 = figure6.add_subplot(111)
    
    inputs_dispatch_6 = {
            "x_data":        assumptions_matrix, 
            "y_data":        power_dispatch_matrix.T / np.sum(demand),
            "ax":            ax6,
            "x_label":       'Time (hour in the year)',
            "y_label":       'Power generation (share of demand)',
            "legend":        legend_list,
            "line_width":    2,
            'grid_option':   0,
            }        
            
    ax6.set_xscale("log", nonposx='clip')
    
    func_stack_plot(inputs_dispatch_6)
    
    pdf_all.savefig(figure6, bbox_inches='tight')
    #plt.close()
    
    # -------------------------------------------------------------------------
    
    # Figure 7 Cost share - power generation
    
    legend_list = sorted(component_index_dispatch.keys(), key=lambda x: x[1])
    
    figure7 = plt.figure(figsize=figsize_oneplot)
    ax7 = figure7.add_subplot(111)
    
    inputs_dispatch_7 = {
            "x_data":        assumptions_matrix, 
            "y_data":        cost_power_matrix.T,
            "ax":            ax7,
            "x_label":       'Time (hour in the year)',
            "y_label":       'Cost contributions ($/kWh)',
            "legend":        legend_list,
            "line_width":    2,
            'grid_option':   0,
            }        
            
    ax7.set_xscale("log", nonposx='clip')
    # ax7.set_yscale("log", nonposx='clip')
    
    ax7.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.2f'))
    
    func_stack_plot(inputs_dispatch_7)
    
    pdf_all.savefig(figure7, bbox_inches='tight')
    #plt.close()
    
    # -------------------------------------------------------------------------
    
    # Figure 8 Cost share - "every type"
    
    legend_list = sorted(component_index_dispatch.keys(), key=lambda x: x[1])
    legend_list.append('storage')
    legend_list.append('unmet demand')
    legend_list.append('curtailment')
    
    figure8 = plt.figure(figsize=figsize_oneplot)
    ax8 = figure8.add_subplot(111)
    
    inputs_dispatch_8 = {
            "x_data":        assumptions_matrix, 
            "y_data":        cost_everything_matrix.T,
            "ax":            ax8,
            "x_label":       'Time (hour in the year)',
            "y_label":       'Cost contributions ($/kWh)',
            "legend":        legend_list,
            "line_width":    2,
            'grid_option':   0,
            }        
            
    ax8.set_xscale("log", nonposx='clip')
    # ax8.set_yscale("log", nonposx='clip')
    
    func_stack_plot(inputs_dispatch_8)
    
    pdf_all.savefig(figure8, bbox_inches='tight')
    #plt.close()
    
    # -------------------------------------------------------------------------
    


#%%
# -----------------------------------------------------------------------------
# func_graphics_dispatch_mix_technology_timeseries_1scenario()
#
# Function: 
#   For a technology, find the week in which the share of demand met by this
#       technology is at maximum or minimum. Then produce 2*2 figures for each
#       such week.
# 
# Input
#   A DICT variable named input_data, with the following keys:
#    demand  -- for editing axes
#   [choice about study scopes]        
#    window_size
#    technology_data   -- the share of demand met by this technology
#    technology_of_interest -- the textual name of this technology
#   [system-level data]
#    results_matrix_dispatch <np.ndarray>
#    results_matrix_demand <np.ndarray>
#    legend_list_dispatch
#    legend_list_demand
#   [options for controling graphical output]      
#    directory_output
#    SAVE_FIGURES_TO_PDF
#    graphics_file_name_prefix
#    graphics_file_name_root
#   [output file]
#    text_file <file> -- an open file stream for outputs
# 
#   dimensions: results_matrix_dispatch, results_matrix_demand
#       row: time_steps
#       column: technology  options or demand types
#        
# Output    
#   2*2 time series figures (line plot, stack plot) * (dispatch mix, demand mix)
#   If you choose to save the files, five files will be saved.
#
# Functions called
#   func_graphics_dispatch_mix_time_selection_1scenario()
#
# History
#   June 22-23, 2018 drafted the function
#
# @ Fan Tong
# -----------------------------------------------------------------------------

def func_graphics_dispatch_mix_technology_timeseries_1scenario(input_data):

    # -------------------------------------------------------------------------
    
    # load the data
    
    demand = input_data['demand']
    
    window_size = input_data['window_size']    
    technology_data = input_data['technology_data']
    technology_of_interest = input_data['technology_of_interest']
    
    results_matrix_dispatch = input_data['results_matrix_dispatch']
    legend_list_dispatch = input_data['legend_list_dispatch']
    results_matrix_demand = input_data['results_matrix_demand']
    legend_list_demand = input_data['legend_list_demand']    
    
    pdf_each = input_data['pdf_each']  # file handle for pdf output    
    text_file = input_data['text_file'] # file handle for text output
    case_name = input_data['case_name']

    # -------------------------------------------------------------------------
    # Define the plotting style
    
    plt.style.use('default')
    # plt.style.use('bmh')
    # plt.style.use('fivethirtyeight')
    # plt.style.use('seaborn-white')
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] =  'Helvetica ' #'Palatino' # 'Ubuntu'
    plt.rcParams['font.monospace'] = 'Helvetica Mono' #'Palatino Mono' # 'Ubuntu'
    plt.rcParams['font.size'] = 16
    plt.rcParams['axes.labelsize'] = 16
    plt.rcParams['axes.labelweight'] = 'bold'
    plt.rcParams['axes.titlesize'] = 16
    plt.rcParams['xtick.labelsize'] = 16
    plt.rcParams['ytick.labelsize'] = 16
    plt.rcParams['legend.fontsize'] = 14
    plt.rcParams['figure.titlesize'] = 16
    plt.rcParams['lines.linewidth'] = 2.0
    plt.rcParams['grid.color'] = 'k'
    plt.rcParams['grid.linestyle'] = ':'
    plt.rcParams['grid.linewidth'] = 0.5
    plt.rcParams['xtick.major.width'] = 2
    plt.rcParams['xtick.major.size'] = 6
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.major.width'] = 2
    plt.rcParams['ytick.major.size'] = 6
    plt.rcParams['ytick.direction'] = 'in'
    
    # -------------------------------------------------------------------------
    
    text_file.write(technology_of_interest)
    text_file.write("\n")
    
    # -------------------------------------------------------------------------
    
    # Time period #1 and #2: maximum and minmum                
    
    study_variable_dict = {
            'window_size':      window_size,
            'data':             technology_data, 
            'print_option':     0,
            }
    
    study_variable_dict['search_option'] = 'max'
    study_output_1 = func_find_period(study_variable_dict)    
    time_range_1 = (study_output_1['left_index'], study_output_1['right_index'])
        
    title_info_1 = (
            technology_of_interest + " met {:.0f} hrs of avg. demand during hours: {}"
            .format(study_output_1['value'], time_range_1)
            )

    text_file.write(
            "{}, {}, {:.1f}\n".format(
                    study_output_1['left_index'], 
                    study_output_1['right_index'],
                    study_output_1['value'])
            )

    # ------------------------------------
    
    study_variable_dict['search_option'] = 'min'
    study_output_2 = func_find_period(study_variable_dict)
    time_range_2 = (study_output_2['left_index'], study_output_2['right_index'])

    title_info_2 = (
            technology_of_interest + " met {:.0f} hrs of avg. demand during hours: {}"
            .format(study_output_2['value'], time_range_2)
            )
    
    text_file.write(
            "{}, {}, {:.1f}\n".format(
                    study_output_2['left_index'], 
                    study_output_2['right_index'],
                    study_output_2['value'])
            )
    
    # -------------------------------------------------------------------------
    
    # Generate graphics - time period #1
        
    # ----------------------------------
    
    # Call the functions to do the work
    
    input_data_1a = {
            "time_range":                   time_range_1,
            "demand_line_for_dispatch_figure":  1,
            "demand":                       demand,
            "mix_matrix":                   results_matrix_dispatch,
            "pdf_each":                    pdf_each,
            "title_text":                   case_name + "Dispatch mix\n" + title_info_1,
            "legend_list":                  legend_list_dispatch,        
            }
    
    func_graphics_dispatch_mix_time_selection_1scenario(input_data_1a)    
    
    input_data_1b = {
            "time_range":                   time_range_1,
            "demand":                       demand,            
            "mix_matrix":                   results_matrix_demand,
            "pdf_each":                    pdf_each,
            "title_text":                   case_name + "Demand mix\n" + title_info_1,
            "legend_list":                  legend_list_demand,        
            }
    
    func_graphics_dispatch_mix_time_selection_1scenario(input_data_1b)    
    
    
    # -------------------------------------------------------------------------
    
    # Generate graphics - time period #2
           
    
    # ----------------------------------
    
    # Call the functions to do the work    
    
    input_data_2a = {
            "time_range":                   time_range_2,
            "demand":                       demand,
            "demand_line_for_dispatch_figure":      1,
            "mix_matrix":                   results_matrix_dispatch,
            "pdf_each":                     pdf_each,
            "title_text":                   case_name + "Dispatch mix\n" + title_info_2,
            "legend_list":                  legend_list_dispatch,        
            }
    
    func_graphics_dispatch_mix_time_selection_1scenario(input_data_2a)    
    
    input_data_2b = {
            "demand":                       demand,
            "time_range":                   time_range_2,        
            "mix_matrix":                   results_matrix_demand,
            "pdf_each":                     pdf_each,
            "title_text":                   case_name + "Demand mix\n" + title_info_2,
            "legend_list":                  legend_list_demand, 
            }
    
    func_graphics_dispatch_mix_time_selection_1scenario(input_data_2b)

    # -------------------------------------------------------------------------
    
          
        
        
#%%
# -----------------------------------------------------------------------------
# func_optimization_results_time_series_1scenario()
#
# Function: 
#   Given the locations (directories or file paths), load the data, perform the
#   the analysis, generate the figures, and save the figures to files.     
# 
# Input
#   A DICT variable named input_data, with the following keys:
#    optimization_results_file_path
#    directory_output
#    graphics_file_name_prefix
#    graphics_file_name_root
#    SAVE_FIGURES_TO_PDF
#
# Output
#   Three groups of figures. If you choose to save the files, five files will be saved.
#       1 dispatch mix and demand mix for all hourly data
#       2 dispatch mix and demand mix for selected ranges of data
#           for technology A (energy storage)
#       3 dispatch mix and demand mix for selected ranges of data
#           for technology B (wind and solar)
#
#   A text file summarizing key information from these technology-focused analyses        
#
# Functions called
#   func_graphics_dispatch_mix_1scenario()
#   func_graphics_dispatch_mix_technology_timeseries_1scenario()
#
# History
#   June 3, 2018 wrote the code
#   June 19, 2018 packaged the code into this function
#   June 20, 2018 modified the part load optimization data
#   June 22-23, 2018 modified the part dealing with selected time periods
#       called the function, func_graphics_dispatch_mix_technology_timeseries_1scenario()
#        
# -----------------------------------------------------------------------------
def get_results_matrix_column(results_matrix,component_list_index_dic,component):
    return results_matrix[:,component_list_index_dic[component]] 

def func_optimization_results_time_series_1scenario(input_data):
    
    # -------------------------------------------------------------------------

    # load the input assumptions


    # -------------------------------------------------------------------------

#    # load the data    
#   
#    temp_dict = func_load_optimization_results(optimization_results_file_path)
#    model_inputs = temp_dict['model_inputs']
#    model_results = temp_dict['model_results']
    
    # -------------------------
    
    demand = input_data['demand']
    results_matrix_dispatch = input_data['results_matrix_dispatch']   
    results_matrix_demand = input_data['results_matrix_demand']
    
    # -------------------------------------------------------------------------
    
    
    legend_list_dispatch = input_data['legend_list_dispatch']    
    legend_list_demand = input_data['legend_list_demand']
    
    component_index_dispatch = input_data['component_index_dispatch']    
    component_index_demand = input_data['component_index_demand']
    
    # -------------------------------------------------------------------------
    
    # Output the "characteristic" time periods and their metrics
    
    # Representative file name
    #   storage_scenario_dispatch_and_demand_mix_1e-2_with_NG_.txt
    
    text_file = input_data['text_file']  # file handle for text file
    
    # -------------------------------------------------------------------------
    
    # Figure group #1 dispatch mix and demand mix for the whole data
    #   using func_graphics_dispatch_mix_1scenario()
    
    # Right now, 12 figures will be generated.
    # 2+2 (supply+demand) figures for each time resolution
    # In total, three time resolutions (hourly, daily, weekly)
        
    
    input_data_1 = {
            "demand":                       demand,
            "results_matrix_dispatch":      results_matrix_dispatch,
            "results_matrix_demand":        results_matrix_demand,
            "pdf_each":                     input_data['pdf_each'],
            "legend_list_dispatch":         legend_list_dispatch,
            "legend_list_demand":           legend_list_demand,
            "case_name":                    input_data["case_name"]
            }
    
    func_graphics_dispatch_mix_1scenario(input_data_1)
    
    # -------------------------------------------------------------------------    

    # Figure group #2 dispatch mix and demand mix for selected time period
    #   technology of interest: energy storage
    #   using func_graphics_dispatch_mix_1scenario()

    dispatch_storage = get_results_matrix_column(results_matrix_dispatch, component_index_dispatch, 'STORAGE')

    technology_data = (dispatch_storage.flatten() / demand.T)
    technology_of_interest = "storage"

    input_data_2 = {
            "window_size":                  24*7,
            "demand":                       demand,
            "technology_data":              technology_data,
            "technology_of_interest":       technology_of_interest,
            
            "results_matrix_dispatch":      results_matrix_dispatch,
            "results_matrix_demand":        results_matrix_demand,
            "legend_list_dispatch":         legend_list_dispatch,
            "legend_list_demand":           legend_list_demand,
            
            "pdf_each":                     input_data['pdf_each'],
            "text_file":                    text_file,
            "case_name":                    input_data["case_name"]
            }

    func_graphics_dispatch_mix_technology_timeseries_1scenario(input_data_2)
    
    # -------------------------------------------------------------------------
    
    # Figure group #3 dispatch mix and demand mix for selected time period
    #   technology of interest: wind and solar
    #   using func_graphics_dispatch_mix_1scenario()
    
    technology_data = ((
            results_matrix_dispatch[:, component_index_dispatch['WIND']] + 
            results_matrix_dispatch[:, component_index_dispatch['SOLAR']]) / demand.T)
            

    input_data_3 = {
            "window_size":                  24*7,
            "demand":                       demand,
            "technology_data":              technology_data,
            "technology_of_interest":       technology_of_interest,
            
            "results_matrix_dispatch":    results_matrix_dispatch,
            "results_matrix_demand":        results_matrix_demand,
            "legend_list_dispatch":         legend_list_dispatch,
            "legend_list_demand":           legend_list_demand,
            
            "pdf_each":                     input_data['pdf_each'],
            "text_file":                    text_file,
            "case_name":                    input_data["case_name"]
            }

    func_graphics_dispatch_mix_technology_timeseries_1scenario(input_data_3)

    # -------------------------------------------------------------------------
    
    # deal with open file streams
    
    text_file.close()

#%%
# -----------------------------------------------------------------------------
# func_optimization_results_system_results_Nscenarios()
#
# Function: generate "representative" results (figures) for a set of optimization 
#   runs whose only difference was due to a change in an assumption.
#
# Input
#   A DICT variable named input_data, that has the following keys
#       optimization_results_file_path_list
#       scenario_list_number
#       SAVE_FIGURES_TO_PDF
#       graphics_file_name
#       directory_output
#       x_label
#   In a nutsheel, these input information tells where to locate the optimization
#       results, what is the distinction across different runs, where to save
#       the generated figures, and how to decorate the figures.
#
# Output
#   A PDF book containing 8 figures.
#   Read the description of func_graphics_system_results_Nscenarios() for details
#
# Functions called
#   func_graphics_system_results_Nscenarios()
#
# History
#   Jun 17, 2018 wrote the code
#   Jun 20, 2018 re-packaged into a function
#       updated the code for loading the data from files    
#
# @ Fan Tong    
# -----------------------------------------------------------------------------

def func_optimization_results_system_results_Nscenarios(input_data):

    # load the input data
    
    optimization_results_file_path_list = input_data['optimization_results_file_path_list']
    scenario_list_number = input_data['scenario_list_number']
    pdf_all = input_data['pdf_all']
    x_label = input_data['x_label']

    # -------------------------------------------------------------------------

    # load the data from scenario to get "component_index_dispatch"
    
    temp_dict = func_load_optimization_results(optimization_results_file_path_list[0])
    model_inputs = temp_dict['model_inputs']
    model_results = temp_dict['model_results']
    
    component_index_dispatch = model_inputs['component_index_dispatch']
    
    # -------------------------------------------------------------------------
    
    # prepare for the loop
    
    # 9 variables (matrix form) to be assembled
    
    storage_capacity_matrix = np.zeros([len(scenario_list_number)])
    storage_dispatch_matrix = np.zeros([len(scenario_list_number)])
    storage_cycle_matrix = np.zeros([len(scenario_list_number)])
    storage_investment_matrix = np.zeros([len(scenario_list_number)])
    
    power_capacity_matrix = np.zeros([len(component_index_dispatch), len(scenario_list_number)])
    power_dispatch_matrix = np.zeros([len(component_index_dispatch), len(scenario_list_number)])
    cost_power_matrix = np.zeros([len(component_index_dispatch), len(scenario_list_number)])
    cost_everything_matrix = np.zeros([len(component_index_dispatch)+3, len(scenario_list_number)])
    
    optimum_cost_matrix = np.zeros([len(scenario_list_number)])
    
    # ----------------------
    
    # loop to extract and "combine" optimization results
    
    for scenario_idx in xrange(len(scenario_list_number)):
    
        # actually load the data
    
        # f = open(optimization_results_file_path_list[scenario_idx], 'rb')
        
        temp_dict = func_load_optimization_results(optimization_results_file_path_list[scenario_idx])
        model_inputs = temp_dict['model_inputs']
        model_results = temp_dict['model_results']
            
        # ---------------------------------------------------------------------
        
        # Energy storage
    
        storage_dispatch_matrix[scenario_idx] = (
            sum(model_results["dispatch_storage"])
            )
        
        storage_capacity_matrix[scenario_idx] = (
            model_results["capacity_storage"]
            )
    
        storage_cycle_matrix[scenario_idx] = (
            sum(model_results["dispatch_storage"]) /
            model_results["capacity_storage"]
            )
        
        storage_investment_matrix[scenario_idx] = (
            model_results["capacity_storage"] * model_inputs['capital_cost_storage']
            )
    
        # ---------------------------------------------------------------------
    
        # Power generation
    
        power_capacity_matrix[:,scenario_idx] = \
            np.reshape(model_results['capacity_power'], -1)
    
        power_dispatch_matrix[:,scenario_idx] = \
            np.reshape(np.sum(model_results['results_matrix_dispatch'], axis=1), -1)
    
        power_dispatch_total = \
            np.sum(model_results['results_matrix_dispatch'], axis = 1)
    
        cost_power_matrix[:,scenario_idx] = (
            ((power_dispatch_total * model_inputs['variable_cost_power'] +
             model_results['capacity_power'] * model_inputs['fixed_cost_power'])
            / np.sum(model_inputs['demand'])))
    
        # ---------------------------------------------------------------------
    
        # Cost breakdown by "everything" (every type)
        # -- power generation technologies, storage, unmet demand, curtailment
    
        storage_dispatch_total = np.sum(model_results['dispatch_storage'])
        storage_charge_total = np.sum(model_results['results_matrix_demand']) 
        
        cost_everything_matrix[0:len(component_index_dispatch),scenario_idx] = (
            cost_power_matrix[:,scenario_idx])
    
        cost_everything_matrix[len(component_index_dispatch)+0,scenario_idx] = (
            (storage_dispatch_total * model_inputs['variable_cost_storage'] +
             storage_charge_total * model_inputs['variable_cost_storage'] +
             model_results["capacity_storage"] * model_inputs['fixed_cost_storage'])
             / np.sum(model_inputs['demand']))
    
        cost_everything_matrix[len(component_index_dispatch)+1,scenario_idx] = (
            np.sum(model_results['unmet_demand']) * model_inputs['unmet_demand_cost']
            / np.sum(model_inputs['demand']))
            
        cost_everything_matrix[len(component_index_dispatch)+2,scenario_idx] = (
            np.sum(model_results['dispatch_curtailment']) * model_inputs['curtailment_cost']
            / np.sum(model_inputs['demand']))
        
        # ---------------------------------------------------------------------
        
        # Optimal system cost
        
        optimum_cost_matrix[scenario_idx] = (
            model_results['optimum'] / np.sum(model_inputs['demand']))
    
    # -------------------------------------------------------------------------
    # Graphics
    
    # Graphics settings
    
    input_data = {
            "component_index_dispatch":             component_index_dispatch,
            "demand":                       model_inputs['demand'],
            "assumptions_matrix":           np.array(scenario_list_number),
            "storage_dispatch_matrix":     storage_dispatch_matrix,
            "storage_capacity_matrix":      storage_capacity_matrix,
            "storage_cycle_matrix":         storage_cycle_matrix,
            "storage_investment_matrix":    storage_investment_matrix,
            "power_capacity_matrix":        power_capacity_matrix,
            "power_dispatch_matrix":        power_dispatch_matrix,
            "cost_power_matrix":            cost_power_matrix,
            "cost_everything_matrix":       cost_everything_matrix,
            "pdf_all":                      input_data['pdf_all'],
            "x_label":                      x_label
            }    

    # call the function to generate figures
    
    func_graphics_system_results_Nscenarios(input_data)

#%%
# -----------------------------------------------------------------------------
# func_optimization_results_dispatch_var_Nscenarios()
#
# Function: generate figures comparing dispatch variables for a technology
#   across a set of optimization runs whose only difference was due to a change
#   in an assumption.
#
# Input
#   A DICT variable named input_data, that has the following keys
#       optimization_results_file_path_list
#       scenario_list_number
#       which_technology_to_all
#       SAVE_FIGURES_TO_PDF
#       graphics_file_name    
#       directory_output
#       title_text
#       legend_list
#   In a nutsheel, these input information tells where to locate the optimization
#       results, what is the distinction across different runs, where to save
#       the generated figures, and how to decorate the figures.
#
# Output
#   A PDF book containing 8 figures.
#   Read the description of func_graphics_dispatch_var_Nscenarios() for details
#
# Functions called
#   func_graphics_dispatch_var_Nscenarios()
#
# History
#   Jun 4, 9, 14, 2018 wrote the code
#   Jun 20, 2018 re-packaged into a function
#       updated the code for loading the data from files  
#    
# @ Fan Tong    
# -----------------------------------------------------------------------------

def func_optimization_results_dispatch_var_Nscenarios(input_data):

    # load the input data
    
    optimization_results_file_path_list = input_data['optimization_results_file_path_list']
    scenario_list_number = input_data['scenario_list_number']
    
    which_technology_to_all = input_data['which_technology_to_all']
    
    pdf_all = input_data['pdf_all']
    title_text = input_data['title_text']
    legend_list = input_data['legend_list']

    # -------------------------------------------------------------------------

    # load the data from scenario to get "component_index_dispatch"
    
    temp_dict = func_load_optimization_results(optimization_results_file_path_list[0])
    model_inputs = temp_dict['model_inputs']
    model_results = temp_dict['model_results']
    
    component_index_dispatch = model_inputs['component_index_dispatch']
    optimization_time_steps = len(model_inputs['demand'])
    
    # -------------------------------------------------------------------------
    
    results_matrix_dispatch = \
        np.zeros([optimization_time_steps, len(scenario_list_number)])
    
    for scenario_idx in xrange(len(scenario_list_number)):

        # actually load the data
            
        temp_dict = func_load_optimization_results(optimization_results_file_path_list[scenario_idx])
        model_inputs = temp_dict['model_inputs']
        model_results = temp_dict['model_results']
        
        if which_technology_to_all == "storage":
            dispatch_results = model_results["dispatch_storage"]
            results_matrix_dispatch[:, scenario_idx] = \
                np.reshape(dispatch_results, -1)
        else:
            dispatch_results = model_results["results_matrix_dispatch"]
            results_matrix_dispatch[:, scenario_idx] = \
                np.reshape(dispatch_results[component_index_dispatch[which_technology_to_all], :], -1)
    
    # -------------------------------------------------------------------------
    
    # Graphics
    
    input_data_1 = {
            "demand":                       model_inputs['demand'],
            "results_matrix_dispatch":      results_matrix_dispatch,
            "directory_output":             directory_output,
            "title_text":                   title_text,
            "legend_list":                  legend_list,
            "pdf_all":                      input_data['pdf_all']
            }
    
    # call the function
    
    func_graphics_dispatch_var_Nscenarios(input_data_1)    