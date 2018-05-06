"""
Post-processing
Created by Lei at 27 March, 2018
"""

# -----------------------------------------------------------------------------

import os,sys
import pickle
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
plt.ioff()

#from matplotlib import style
#style.use('ggplot')

color_natgas  = {0:"red",    1:"tomato"}
color_solar   = {0:"orange", 1:"wheat"}
color_wind    = {0:"blue",   1:"skyblue"}
color_nuclear = {0:"green",  1:"limegreen"}
color_storage = {0:"m",      1:"orchid"}

#===============================================================================
#================================================= DEFINITION SECTION ==========
#===============================================================================

def unpickle_raw_results(
        file_path_name,
        verbose
        ):
    
    with open(file_path_name, 'rb') as db:
       file_info, time_series, assumption_list, result_list = pickle.load (db)
    if verbose:
        print 'data unpickled from '+file_path_name
    return file_info, time_series, assumption_list, result_list

def get_dimension_info(assumption_list):
    fix_cost_natgas = []
    fix_cost_solar = []
    fix_cost_wind = []
    fix_cost_nuclear = []
    fix_cost_storage = []
    
    var_cost_natgas = []
    var_cost_solar = []
    var_cost_wind = []
    var_cost_nuclear = []
    var_cost_storage = []
    
    num_scenarios = len(assumption_list)
    for idx in range(num_scenarios):
        fix_cost_natgas  = np.r_[fix_cost_natgas,  assumption_list[idx]['fix_cost_natgas']]
        fix_cost_solar   = np.r_[fix_cost_solar,   assumption_list[idx]['fix_cost_solar']]
        fix_cost_wind    = np.r_[fix_cost_wind,    assumption_list[idx]['fix_cost_wind']]
        fix_cost_nuclear = np.r_[fix_cost_nuclear, assumption_list[idx]['fix_cost_nuclear']]
        fix_cost_storage = np.r_[fix_cost_storage, assumption_list[idx]['fix_cost_storage']]
    
        var_cost_natgas  = np.r_[var_cost_natgas,  assumption_list[idx]['var_cost_natgas']]
        var_cost_solar   = np.r_[var_cost_solar,   assumption_list[idx]['var_cost_solar']]
        var_cost_wind    = np.r_[var_cost_wind,    assumption_list[idx]['var_cost_wind']]
        var_cost_nuclear = np.r_[var_cost_nuclear, assumption_list[idx]['var_cost_nuclear']]
        var_cost_storage = np.r_[var_cost_storage, assumption_list[idx]['var_cost_storage']]
        
    fix_cost_natgas_list  = np.unique(fix_cost_natgas)
    fix_cost_solar_list   = np.unique(fix_cost_solar)
    fix_cost_wind_list    = np.unique(fix_cost_wind)
    fix_cost_nuclear_list = np.unique(fix_cost_nuclear)
    fix_cost_storage_list = np.unique(fix_cost_storage)
    
    var_cost_natgas_list  = np.unique(var_cost_natgas)
    var_cost_solar_list   = np.unique(var_cost_solar)
    var_cost_wind_list    = np.unique(var_cost_wind)
    var_cost_nuclear_list = np.unique(var_cost_nuclear)
    var_cost_storage_list = np.unique(var_cost_storage)
    
    cost_list = {'fix_cost_natgas':fix_cost_natgas_list,
                 'fix_cost_solar':fix_cost_solar_list,
                 'fix_cost_wind':fix_cost_wind_list,
                 'fix_cost_nuclear':fix_cost_nuclear_list,
                 'fix_cost_storage':fix_cost_storage_list,
                 'var_cost_natgas':var_cost_natgas_list,
                 'var_cost_solar':var_cost_solar_list,
                 'var_cost_wind':var_cost_wind_list,
                 'var_cost_nuclear':var_cost_nuclear_list,
                 'var_cost_storage':var_cost_storage_list}
    var_list = ['fix_cost_natgas',
                'fix_cost_solar',
                'fix_cost_wind',
                'fix_cost_nuclear',
                'fix_cost_storage',
                'var_cost_natgas',
                'var_cost_solar',
                'var_cost_wind',
                'var_cost_nuclear',
                'var_cost_storage',]
    
    return cost_list, var_list

def prepare_scalar_variables (
        file_info,
        time_series,
        assumption_list,
        result_list,
        verbose
        ):
    
    num_scenarios    = len(assumption_list)
    res = {}

    # put all scenarios data in one list res;
    for idx in range(num_scenarios):
        tmp = {}
        
        tmp['demand']         = np.array(np.squeeze(time_series['demand_series'])) #/ num_time_periods
        tmp['solar_capacity'] = np.array(np.squeeze(time_series['solar_series']))  #/ num_time_periods
        tmp['wind_capacity']  = np.array(np.squeeze(time_series['wind_series']))   #/ num_time_periods
        tmp['fix_cost_natgas']  = np.array(np.squeeze(assumption_list[idx]['fix_cost_natgas']))
        tmp['fix_cost_solar']   = np.array(np.squeeze(assumption_list[idx]['fix_cost_solar']))
        tmp['fix_cost_wind']    = np.array(np.squeeze(assumption_list[idx]['fix_cost_wind']))
        tmp['fix_cost_nuclear'] = np.array(np.squeeze(assumption_list[idx]['fix_cost_nuclear']))
        tmp['fix_cost_storage'] = np.array(np.squeeze(assumption_list[idx]['fix_cost_storage']))
        tmp['var_cost_natgas']        = np.array(np.squeeze(assumption_list[idx]['var_cost_natgas']))
        tmp['var_cost_solar']         = np.array(np.squeeze(assumption_list[idx]['var_cost_solar']))
        tmp['var_cost_wind']          = np.array(np.squeeze(assumption_list[idx]['var_cost_wind']))
        tmp['var_cost_nuclear']       = np.array(np.squeeze(assumption_list[idx]['var_cost_nuclear']))
        tmp['var_cost_storage']       = np.array(np.squeeze(assumption_list[idx]['var_cost_storage']))
        tmp['var_cost_dispatch_to_storage']    = np.array(np.squeeze(assumption_list[idx]['var_cost_dispatch_to_storage']))
        tmp['var_cost_dispatch_from_storage']  = np.array(np.squeeze(assumption_list[idx]['var_cost_dispatch_from_storage']))
        tmp['var_cost_unmet_demand']  = np.array(np.squeeze(assumption_list[idx]['var_cost_unmet_demand']))
        tmp['capacity_natgas']  = np.array(np.squeeze(result_list[idx]['capacity_natgas']))
        tmp['capacity_solar']   = np.array(np.squeeze(result_list[idx]['capacity_solar']))
        tmp['capacity_wind']    = np.array(np.squeeze(result_list[idx]['capacity_wind']))
        tmp['capacity_nuclear'] = np.array(np.squeeze(result_list[idx]['capacity_nuclear']))
        tmp['capacity_storage'] = np.array(np.squeeze(result_list[idx]['capacity_storage']))
        tmp['dispatch_natgas']        = np.array(np.squeeze(result_list[idx]['dispatch_natgas']))       #/ num_time_periods
        tmp['dispatch_solar']         = np.array(np.squeeze(result_list[idx]['dispatch_solar']))        #/ num_time_periods
        tmp['dispatch_wind']          = np.array(np.squeeze(result_list[idx]['dispatch_wind']))         #/ num_time_periods
        tmp['dispatch_nuclear']       = np.array(np.squeeze(result_list[idx]['dispatch_nuclear']))      #/ num_time_periods
        tmp['dispatch_to_storage']    = np.array(np.squeeze(result_list[idx]['dispatch_to_storage']))   #/ num_time_periods
        tmp['dispatch_from_storage']  = np.array(np.squeeze(result_list[idx]['dispatch_from_storage'])) #/ num_time_periods
        tmp['dispatch_unmet_demand']  = np.array(np.squeeze(result_list[idx]['dispatch_unmet_demand'])) #/ num_time_periods
        tmp['dispatch_curtailment']   = np.array(np.squeeze(result_list[idx]['dispatch_curtailment']))  #/ num_time_periods
        tmp['energy_storage']         = np.array(np.squeeze(result_list[idx]['energy_storage']))        #/ num_time_periods
        tmp['system_cost']    = np.array(np.squeeze(result_list[idx]['system_cost']))  
        tmp['storage_charging_efficiency']    = np.array(np.squeeze(assumption_list[idx]['storage_charging_efficiency']))

        res[idx] = tmp
    return res

#------------------------------------------------------------------------------
#------------------------------------------------ Plotting function -----------
#------------------------------------------------------------------------------   

def get_multicases_results(res, num_case, var, *avg_option):    
    x = []
    for idx in range(num_case):
        tmp_var = res[idx][var]
        x.append(np.array(tmp_var))
    if avg_option:
        y = avg_series(x, 
                       num_case,
                       avg_option[0], 
                       avg_option[1], 
                       avg_option[2],
                       avg_option[3])
        return y
    else:
        return np.array(x)

def avg_series(var, num_case, beg_step, end_step, nstep, num_return):
    x = []
    y = []
    if num_case > 1:
        for idx in range(num_case):
            hor_mean = np.mean(var[idx][beg_step-1:end_step].reshape(-1,nstep),axis=1)
            ver_mean = np.mean(var[idx][beg_step-1:end_step].reshape(-1,nstep),axis=0)
            x.append(hor_mean)
            y.append(ver_mean)
    else:
        hor_mean = np.mean(var[beg_step-1:end_step].reshape(-1,nstep),axis=1)
        ver_mean = np.mean(var[beg_step-1:end_step].reshape(-1,nstep),axis=0)
        x.append(hor_mean)
        y.append(ver_mean)
    if num_return == 1:
        return np.array(x)
    if num_return == 2:
        return np.array(y)

def cal_cost(fix_cost, capacity,
             var_cost, dispatch,
             num_case, num_time_periods,
             *battery_dispatch):
    
    cost_fix = np.array(fix_cost * capacity)
    
    cost_var = np.zeros(num_case)
    for idx in range(num_case):
        if battery_dispatch:
            cost_var_tmp = var_cost[idx]       * np.sum(dispatch[idx]) + \
                           np.array(battery_dispatch[0][idx]) * np.sum(np.array(battery_dispatch[1][idx])) +\
                           np.array(battery_dispatch[2][idx]) * np.sum(np.array(battery_dispatch[3][idx]))
        else:
            cost_var_tmp = var_cost[idx] * np.sum(dispatch[idx]) 
        cost_var[idx] = cost_var_tmp
        
    cost_tot = cost_fix + cost_var
    return cost_fix, cost_var, cost_tot

# --------- stack plot1
def plot_multi_panels1(ax,case):
    ax.grid(True, color='k', linestyle='--', alpha=0.2)
    ax.set_axis_bgcolor('white')
    
    ax.stackplot(case[0], case[1], colors=case[4], baseline = 'zero', alpha = 0.5)
    ax.stackplot(case[0], case[2], labels=case[3], colors=case[4],  baseline = 'zero', alpha = 0.5)
    if len(case) == 7:
        ax.plot(case[0], np.array(case[6][0]),c='r', linewidth = '1', linestyle='-', label='charge')
        ax.plot(case[0], np.array(case[6][1]),c='g', linewidth = '1', linestyle='-', label='discharge')
        ax.fill_between(case[0], np.array(case[6][0]), np.array(case[6][1]), facecolor='black', alpha=0.2, label='energy loss')
    y_line = np.zeros(case[2].shape[1])
    for idx in range(int(case[2].shape[0])):
        y_line = y_line + case[2][idx]
        ax.plot(case[0], y_line, c='k', linewidth = 0.5)
    
    ax.set_xlim(case[0][-1],case[0][0])
    for label in ax.xaxis.get_ticklabels():
        label.set_rotation(45)
    ax.set_xlabel(case[5]["xlabel"],fontsize=9)
    ax.set_title(case[5]["title"],fontsize=9)   
    ax.spines['right'].set_color('black')
    ax.spines['top'].set_color('black')
    ax.spines['left'].set_color('black')
    ax.spines['bottom'].set_color('black')
    
    leg = ax.legend(loc='center left', ncol=1, 
                    bbox_to_anchor=(1, 0.5), prop={'size': 5})
    leg.get_frame().set_alpha(0.4)
    
def plot_stack_multi1(case1,case2,case3,case4, case_name):
    fig, axes = plt.subplots(2,2)
    fig.subplots_adjust(top=1, left=0.0, right=1, hspace=0.5, wspace=0.35)
    ((ax1, ax2), (ax3, ax4)) = axes
    
    plot_multi_panels1(ax1,case1)
    plot_multi_panels1(ax2,case2)
    plot_multi_panels1(ax3,case3)
    plot_multi_panels1(ax4,case4)
    plt.setp(ax1.get_xticklabels(), size=7)
    plt.setp(ax2.get_xticklabels(), size=7)
    plt.setp(ax3.get_xticklabels(), size=7)
    plt.setp(ax4.get_xticklabels(), size=7)
    ax1.set_xlabel('')
    ax2.set_xlabel('')
    plt.setp(ax1.get_yticklabels(), size=7)
    plt.setp(ax2.get_yticklabels(), size=7)
    plt.setp(ax3.get_yticklabels(), size=7)
    plt.setp(ax4.get_yticklabels(), size=7)

    return fig
    plt.close(fig)

def stack_plot1(
        res,
        num_case,
        case_name,
        multipanel,
        var_dimension_list):
    
    # --- get Raw Data ---
    num_time_periods = len(res[0]['demand'])

    solar_series      = get_multicases_results(res, num_case , 'solar_capacity')   / num_time_periods
    wind_series       = get_multicases_results(res, num_case , 'wind_capacity')    / num_time_periods
    var_dimension = get_multicases_results(res, num_case, var_dimension_list[0])
    capacity_natgas   = get_multicases_results(res, num_case , 'capacity_natgas')
    capacity_solar    = get_multicases_results(res, num_case , 'capacity_solar')
    capacity_wind     = get_multicases_results(res, num_case , 'capacity_wind')
    capacity_nuclear  = get_multicases_results(res, num_case , 'capacity_nuclear')
    capacity_storage  = get_multicases_results(res, num_case , 'capacity_storage')    
    fix_cost_natgas  = get_multicases_results(res, num_case, 'fix_cost_natgas')
    fix_cost_solar   = get_multicases_results(res, num_case, 'fix_cost_solar')
    fix_cost_wind    = get_multicases_results(res, num_case, 'fix_cost_wind')
    fix_cost_nuclear = get_multicases_results(res, num_case, 'fix_cost_nuclear')
    fix_cost_storage = get_multicases_results(res, num_case, 'fix_cost_storage')    
    var_cost_natgas  = get_multicases_results(res, num_case, 'var_cost_natgas')
    var_cost_solar   = get_multicases_results(res, num_case, 'var_cost_solar')
    var_cost_wind    = get_multicases_results(res, num_case, 'var_cost_wind')
    var_cost_nuclear = get_multicases_results(res, num_case, 'var_cost_nuclear')
    var_cost_storage = get_multicases_results(res, num_case, 'var_cost_storage') 
    var_cost_dispatch_to_storage   = get_multicases_results(res, num_case, 'var_cost_dispatch_to_storage') 
    var_cost_dispatch_from_storage = get_multicases_results(res, num_case, 'var_cost_dispatch_from_storage')     
    dispatch_natgas       = get_multicases_results(res, num_case, 'dispatch_natgas')        / num_time_periods
    dispatch_solar        = get_multicases_results(res, num_case, 'dispatch_solar')         / num_time_periods
    dispatch_wind         = get_multicases_results(res, num_case, 'dispatch_wind')          / num_time_periods
    dispatch_nuclear      = get_multicases_results(res, num_case, 'dispatch_nuclear')       / num_time_periods
    dispatch_to_storage   = get_multicases_results(res, num_case, 'dispatch_to_storage')    / num_time_periods
    dispatch_from_storage = get_multicases_results(res, num_case, 'dispatch_from_storage')  / num_time_periods
    energy_storage        = get_multicases_results(res, num_case, 'energy_storage')         / num_time_periods

    # --- global setting ---
    order_list = fix_cost_nuclear.argsort()  
    xaxis = var_dimension[order_list]
    
    # -plot1: capacity-
    yaxis_capacity_ne = np.zeros(num_case)
    yaxis_capacity_po = np.vstack([capacity_natgas[order_list], 
                                   capacity_solar[order_list], 
                                   capacity_wind[order_list],
                                   capacity_nuclear[order_list],
                                   capacity_storage[order_list]])
    labels_capacity = ["natgas", "solar", "wind", "nuclear", "storage"]
    colors_capacity = [color_natgas[1], color_solar[1], color_wind[1], color_nuclear[1], color_storage[1]]
    info_capacity = {
            "title": "Capacity mix\n(kW)",
            "xlabel": var_dimension_list[0],
            "ylabel": "Capacity (kW)",
            "fig_name": "Capacity_mix"}    

    # -plot2: total dispatch 
    dispatch_tot_natgas  = np.sum(dispatch_natgas,axis=1)
    dispatch_tot_solar   = np.sum(dispatch_solar,axis=1)
    dispatch_tot_wind    = np.sum(dispatch_wind,axis=1)
    dispatch_tot_nuclear = np.sum(dispatch_nuclear,axis=1)
    dispatch_tot_to_storage   = np.sum(dispatch_to_storage,axis=1)
    dispatch_tot_from_storage = np.sum(dispatch_from_storage,axis=1)
    
    curtail_tot_natgas  = capacity_natgas - dispatch_tot_natgas
    curtail_tot_solar   = capacity_solar * np.sum(solar_series,axis=1) - dispatch_tot_solar
    curtail_tot_wind    = capacity_wind  * np.sum(wind_series,axis=1)  - dispatch_tot_wind
    curtail_tot_nuclear = capacity_nuclear - dispatch_tot_nuclear    
            
    yaxis_dispatch_ne = np.vstack([curtail_tot_natgas[order_list]   * (-1),
                                   curtail_tot_solar[order_list]    * (-1),
                                   curtail_tot_wind[order_list]     * (-1),
                                   curtail_tot_nuclear[order_list]  * (-1)
                                   ])        
    yaxis_dispatch_po = np.vstack([dispatch_tot_natgas[order_list], 
                                   dispatch_tot_solar[order_list], 
                                   dispatch_tot_wind[order_list],
                                   dispatch_tot_nuclear[order_list]])
    battery_charge = np.array([dispatch_tot_to_storage, dispatch_tot_from_storage])
    
    labels_dispatch = ["natgas", "solar", "wind", "nuclear"]
    colors_dispatch = [color_natgas[1], color_solar[1], color_wind[1], color_nuclear[1]]    
    info_dispatch = {
            "title": "Total dispatched energy\n(kWh)",
            "xlabel": var_dimension_list[0],
            "ylabel": "Total dispatch (KWh)",
            "fig_name": "Total_dispatch_mix"}   
    
    # -plot3: system_cost
    cost_natgas  = cal_cost(fix_cost_natgas,  capacity_natgas,  var_cost_natgas,  dispatch_natgas,  num_case, num_time_periods)
    cost_solar   = cal_cost(fix_cost_solar,   capacity_solar,   var_cost_solar,   dispatch_solar,   num_case, num_time_periods)
    cost_wind    = cal_cost(fix_cost_wind,    capacity_wind,    var_cost_wind,    dispatch_wind,    num_case, num_time_periods)
    cost_nuclear = cal_cost(fix_cost_nuclear, capacity_nuclear, var_cost_nuclear, dispatch_nuclear, num_case, num_time_periods)
    cost_storage = cal_cost(fix_cost_storage, capacity_storage, var_cost_storage, energy_storage,num_case, num_time_periods, 
                            var_cost_dispatch_to_storage,  dispatch_to_storage,
                            var_cost_dispatch_from_storage,dispatch_from_storage)  # now dispatch_to/from is free    
    
    yaxis_cost_ne = np.zeros(num_case)
    yaxis_cost1_po = np.vstack([cost_natgas[2][order_list], 
                                cost_solar[2][order_list], 
                                cost_wind[2][order_list],
                                cost_nuclear[2][order_list],
                                cost_storage[2][order_list]])
    labels_cost1 = ["natgas", "solar", "wind", "nuclear", "storage"]
    colors_cost1 = [color_natgas[1], color_solar[1], color_wind[1], color_nuclear[1], color_storage[1]]
    info_cost1 = {
            "title": "System cost\n($/kW/h)",
            "xlabel": var_dimension_list[0],
            "ylabel": "System cost ($/kW/h)",
            "fig_name": "System_cost_total"} 
    
    # -plot4: system_cost
    yaxis_cost2_po = np.vstack([cost_natgas[0][order_list],
                                cost_natgas[1][order_list],
                                cost_solar[0][order_list],
                                cost_solar[1][order_list],
                                cost_wind[0][order_list],
                                cost_wind[1][order_list],
                                cost_nuclear[0][order_list],
                                cost_nuclear[1][order_list],
                                cost_storage[0][order_list],
                                cost_storage[1][order_list]]) 
    labels_cost2 = ["natgas_fix",  'natgas_var', 
                    "solar_fix",   'solar_var', 
                    "wind_fix",    'wind_var', 
                    "nuclear_fix", 'nuclear_var', 
                    "storage_fix", 'storage_var',
                    ]
    colors_cost2 = [color_natgas[1],  color_natgas[0],
                    color_solar[1],   color_solar[0], 
                    color_wind[1],    color_wind[0],
                    color_nuclear[1], color_nuclear[0], 
                    color_storage[1], color_storage[0]
                    ]
    info_cost2 = {
            "title": "System cost\n($/kW/h)",
            "xlabel": var_dimension_list[0],
            "ylabel": "System cost ($/kW/h)",
            "fig_name": "System_cost_seperate"} 
    
    plot_case1 = [xaxis, yaxis_capacity_ne, yaxis_capacity_po, labels_capacity, colors_capacity, info_capacity]
    plot_case2 = [xaxis, yaxis_dispatch_ne, yaxis_dispatch_po, labels_dispatch, colors_dispatch, info_dispatch, battery_charge] 
    plot_case3 = [xaxis, yaxis_cost_ne, yaxis_cost1_po, labels_cost1, colors_cost1, info_cost1]
    plot_case4 = [xaxis, yaxis_cost_ne, yaxis_cost2_po, labels_cost2, colors_cost2, info_cost2]   
    
    if multipanel:
        plotx = plot_stack_multi1(plot_case1, plot_case2, plot_case3, plot_case4, case_name)
    else:
        print 'please use multipanel = True!'

    return plotx

# --------- stack plot2
def plot_multi_panels2(ax,case):
    ax.grid(True, color='k', linestyle='--', alpha=0.2)
    ax.set_axis_bgcolor('white')
    
    ax.stackplot(case[0], case[1], colors=case[4], baseline = 'zero', alpha = 0.5)
    ax.stackplot(case[0], case[2], labels=case[3], colors=case[4],  baseline = 'zero', alpha = 0.5)
    ax.plot(case[0], case[5], c='k', linewidth = 1.5, linestyle = '-', label = 'demand')  
    total_energy_gen = np.sum(case[2][:-1,:],axis=0)
    ax.fill_between(case[0],case[5],total_energy_gen, case[5]<total_energy_gen, alpha = 0.0)        
    
    y_line = np.zeros(case[2].shape[1])
    for idx in range(int(case[2].shape[0])):
        y_line = y_line + case[2][idx]
        ax.plot(case[0], y_line, c='grey', linewidth = 0.5)
    y_line = np.zeros(case[1].shape[1])
    for idx in range(int(case[1].shape[0])):
        y_line = y_line + case[1][idx]
        ax.plot(case[0], y_line, c='grey', linewidth = 0.5)
        
    ax.set_xlim(case[0][0],case[0][-1])
    for label in ax.xaxis.get_ticklabels():
        label.set_rotation(45)
    ax.set_xlabel(case[6]["xlabel"],fontsize=9)
    ax.set_title(case[6]["title"],fontsize=9)   
    ax.spines['right'].set_color('black')
    ax.spines['top'].set_color('black')
    ax.spines['left'].set_color('black')
    ax.spines['bottom'].set_color('black')
    
    leg = ax.legend(loc='center left', ncol=1, 
                    bbox_to_anchor=(1, 0.5), prop={'size': 5})
    leg.get_frame().set_alpha(0.4)
    
def plot_stack_multi2(case1,case2,case3, case_name):
    fig = plt.figure()
    fig.subplots_adjust(top=1, left=0.0, right=1, hspace=0.7, wspace=0.35)
    
    ax1 = plt.subplot2grid((2,2),(0,0),rowspan=1, colspan=2)
    plot_multi_panels2(ax1,case1)
    ax2 = plt.subplot2grid((2,2),(1,0),rowspan=1, colspan=1)
    plot_multi_panels2(ax2,case2)
    ax3 = plt.subplot2grid((2,2),(1,1),rowspan=1, colspan=1,sharey=ax2)
    plot_multi_panels2(ax3,case3)

    plt.setp(ax1.get_xticklabels(), size=7)
    plt.setp(ax2.get_xticklabels(), size=7)
    plt.setp(ax3.get_xticklabels(), size=7)
    plt.setp(ax1.get_yticklabels(), size=7)
    plt.setp(ax2.get_yticklabels(), size=7)
    plt.setp(ax3.get_yticklabels(), size=7)

    return fig
    plt.close(fig)
    
def stack_plot2(
        res,
        num_case,
        case_name,
        multipanel,
        var_dimension_list,
        *select_case):
    
    # --- data preparation ---
    num_time_periods = len(res[0]['demand'])
    
    find_case_idx = False
    if select_case:
        var1 = get_multicases_results(res, num_case , select_case[0][0])
        var2 = get_multicases_results(res, num_case , select_case[0][1])
        for idx in range(num_case):
            if var1[idx] == select_case[1][0] and var2[idx] == select_case[1][1]:
                find_case_idx = True
                case_idx = idx
                break
                
        if find_case_idx: 
            print 'Find case index:', case_idx
        else:
            print 'Error: no such case'
            sys.exit(0)
        
    if find_case_idx == False:
        case_idx = 0
    
    capacity_natgas   = get_multicases_results(res, num_case , 'capacity_natgas')[case_idx]
    how_many_case = int(capacity_natgas.size)
    if how_many_case > 1:
        print "too many case for time path plot"
        sys.exit(0)
    
    capacity_solar    = get_multicases_results(res, num_case , 'capacity_solar')[case_idx]
    capacity_wind     = get_multicases_results(res, num_case , 'capacity_wind')[case_idx]
    capacity_nuclear  = get_multicases_results(res, num_case , 'capacity_nuclear')[case_idx]
    demand_yr = get_multicases_results(res, num_case , 'demand'   ,1,num_time_periods,24,1)[case_idx]
    demand_day1 = get_multicases_results(res, num_case , 'demand'   ,3601,4320,24,2)[case_idx]
    demand_day2 = get_multicases_results(res, num_case , 'demand'   ,7921,8640,24,2)[case_idx]    
    solar_series_yr = get_multicases_results(res, num_case , 'solar_capacity'   ,1,num_time_periods,24,1)[case_idx]
    solar_series_day1 = get_multicases_results(res, num_case , 'solar_capacity' ,3601,4320,24,2)[case_idx]
    solar_series_day2 = get_multicases_results(res, num_case , 'solar_capacity' ,7921,8640,24,2)[case_idx]
    wind_series_yr  = get_multicases_results(res, num_case , 'wind_capacity'   ,1,num_time_periods,24,1)[case_idx]
    wind_series_day1  = get_multicases_results(res, num_case , 'wind_capacity' ,3601,4320,24,2)[case_idx]
    wind_series_day2  = get_multicases_results(res, num_case , 'wind_capacity' ,7921,8640,24,2)[case_idx]
    dispatch_natgas_yr  = get_multicases_results(res, num_case,      'dispatch_natgas',      1,num_time_periods,24,1)[case_idx]
    dispatch_solar_yr   = get_multicases_results(res, num_case,      'dispatch_solar',       1,num_time_periods,24,1)[case_idx]     
    dispatch_wind_yr    = get_multicases_results(res, num_case,      'dispatch_wind',        1,num_time_periods,24,1)[case_idx]          
    dispatch_nuclear_yr = get_multicases_results(res, num_case,      'dispatch_nuclear',     1,num_time_periods,24,1)[case_idx]  
    dispatch_from_storage_yr = get_multicases_results(res, num_case, 'dispatch_from_storage',1,num_time_periods,24,1)[case_idx]
    dispatch_natgas_day1  = get_multicases_results(res, num_case,      'dispatch_natgas',      3601,4320,24,2)[case_idx]     
    dispatch_solar_day1   = get_multicases_results(res, num_case,      'dispatch_solar',       3601,4320,24,2)[case_idx]     
    dispatch_wind_day1    = get_multicases_results(res, num_case,      'dispatch_wind',        3601,4320,24,2)[case_idx]          
    dispatch_nuclear_day1 = get_multicases_results(res, num_case,      'dispatch_nuclear',     3601,4320,24,2)[case_idx]  
    dispatch_from_storage_day1 = get_multicases_results(res, num_case, 'dispatch_from_storage',3601,4320,24,2)[case_idx]    
    dispatch_natgas_day2  = get_multicases_results(res, num_case,      'dispatch_natgas',      7921,8640,24,2)[case_idx]     
    dispatch_solar_day2   = get_multicases_results(res, num_case,      'dispatch_solar',       7921,8640,24,2)[case_idx]     
    dispatch_wind_day2    = get_multicases_results(res, num_case,      'dispatch_wind',        7921,8640,24,2)[case_idx]          
    dispatch_nuclear_day2 = get_multicases_results(res, num_case,      'dispatch_nuclear',     7921,8640,24,2)[case_idx]  
    dispatch_from_storage_day2 = get_multicases_results(res, num_case, 'dispatch_from_storage',7921,8640,24,2)[case_idx] 
    curtail_natgas_yr  = capacity_natgas                    - dispatch_natgas_yr
    curtail_solar_yr   = capacity_solar   * solar_series_yr - dispatch_solar_yr
    curtail_wind_yr    = capacity_wind    * wind_series_yr  - dispatch_wind_yr
    curtail_nuclear_yr = capacity_nuclear                   - dispatch_nuclear_yr
    curtail_natgas_day1  = capacity_natgas                      - dispatch_natgas_day1
    curtail_solar_day1   = capacity_solar   * solar_series_day1 - dispatch_solar_day1
    curtail_wind_day1    = capacity_wind    * wind_series_day1  - dispatch_wind_day1
    curtail_nuclear_day1 = capacity_nuclear                     - dispatch_nuclear_day1
    curtail_natgas_day2  = capacity_natgas                      - dispatch_natgas_day2
    curtail_solar_day2   = capacity_solar   * solar_series_day2 - dispatch_solar_day2
    curtail_wind_day2    = capacity_wind    * wind_series_day2  - dispatch_wind_day2
    curtail_nuclear_day2 = capacity_nuclear                     - dispatch_nuclear_day2
    # Now plot
    xaxis_yr = np.arange(360)+1
    yaxis_yr_ne = np.vstack([curtail_natgas_yr*(-1),
                             curtail_solar_yr*(-1),
                             curtail_wind_yr*(-1),
                             curtail_nuclear_yr*(-1),
                             curtail_natgas_yr*0.0
                             ])
    yaxis_yr_po = np.vstack([dispatch_natgas_yr,
                             dispatch_solar_yr,
                             dispatch_wind_yr,
                             dispatch_nuclear_yr,
                             dispatch_from_storage_yr
                             ]) 
        
    opccinfo1 = select_case[0][0]+'='+str(select_case[1][0])
    opccinfo2 = select_case[0][1]+'='+str(select_case[1][1])
    
    labels = ["natgas", "solar", "wind", "nuclear","discharge"]
    colors = [color_natgas[1], color_solar[1], color_wind[1], color_nuclear[1], color_storage[1]]    
    info_yr = {
            "title": "Daily-average per hour dispatch (kWh)\n(For central case:  " + opccinfo1+';  '+opccinfo2+')',
            "xlabel": "time step (day)",
            "ylabel": "",
            "fig_name": "dispatch_case"}
    
    xaxis_day = np.arange(24)+1
    yaxis_day1_ne = np.vstack([curtail_natgas_day1*(-1),
                               curtail_solar_day1*(-1),
                               curtail_wind_day1*(-1),
                               curtail_nuclear_day1*(-1),
                               curtail_natgas_day1*0.0
                               ])
    yaxis_day1_po = np.vstack([dispatch_natgas_day1,
                               dispatch_solar_day1,
                               dispatch_wind_day1,
                               dispatch_nuclear_day1,
                               dispatch_from_storage_day1
                               ]) 
    info_day1 = {
            "title": "Hourly-average per hour dispatch (kWh)\n(June)",
            "xlabel": "time step (hour)",
            "ylabel": "",
            "fig_name": "dispatch_case"}   
    
    yaxis_day2_ne = np.vstack([curtail_natgas_day2*(-1),
                               curtail_solar_day2*(-1),
                               curtail_wind_day2*(-1),
                               curtail_nuclear_day2*(-1),
                               curtail_natgas_day2*0.0
                               ])
    yaxis_day2_po = np.vstack([dispatch_natgas_day2,
                               dispatch_solar_day2,
                               dispatch_wind_day2,
                               dispatch_nuclear_day2,
                               dispatch_from_storage_day2
                               ]) 
    info_day2 = {
            "title": "Hourly-average per hour dispatch (kWh)\n(December)",
            "xlabel": "time step (hour)",
            "ylabel": "",
            "fig_name": "dispatch_case"}  
    if multipanel:
        plot_case1 = [xaxis_yr, yaxis_yr_ne,yaxis_yr_po,labels, colors, demand_yr, info_yr]
        plot_case2 = [xaxis_day, yaxis_day1_ne,yaxis_day1_po,labels, colors, demand_day1, info_day1]
        plot_case3 = [xaxis_day, yaxis_day2_ne,yaxis_day2_po,labels, colors, demand_day2, info_day2]
        ploty = plot_stack_multi2(plot_case1,plot_case2,plot_case3,case_name)
    else:
        print 'please use multipanel = True!'
    return ploty
    
# --------- contour plot
    
def plot_contour(x,y,z,levels,var_dimension):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    cs1 = ax.contourf(x,y,z,levels=levels,
                      cmap='PuBu_r',
                      extend='both')
    cs2 = ax.contour(x,y,z,levels=levels[::4],
                     colors='k',
                     linewidths=0.5, 
                     alpha=1.)
    ax.clabel(cs2, inline=1, fontsize=5)
    
    plt.colorbar(cs1, ticks=levels[::2], orientation='vertical')    
    ax.set_title('system_cost\n($)')
    ax.set_xlabel(var_dimension[0])
    ax.set_ylabel(var_dimension[1]) 
    ax.set_xlim(x.max(),x.min())
    return fig
    plt.clf()

def create_contour_axes(x,y,z):
    
    def find_z(x_need, y_need):
        tot_idx = len(x)
        for idx in range(tot_idx):
            if x[idx] == x_need and y[idx] == y_need:
                find_z = z[idx]
        return find_z
    
    x_uni = np.unique(x)
    y_uni = np.unique(y)
    z2 = np.ones([ len(x_uni), len(y_uni) ])* (-9999)
    for idx_x in range( len(x_uni) ):
        for idx_y in range( len(y_uni) ):
            x_need = x_uni[idx_x]
            y_need = y_uni[idx_y]
            z2[idx_x, idx_y] = find_z(x_need,y_need)
    z3 = np.ma.masked_values(z2, -9999)
    return x_uni, y_uni, z3

def contour_plot(res,num_case,case_name,var_dimension):
    dimension1 = get_multicases_results(res, num_case, var_dimension[0])
    dimension2 = get_multicases_results(res, num_case, var_dimension[1])
    system_cost      = get_multicases_results(res, num_case, 'system_cost')
    x,y,z = create_contour_axes(dimension1, dimension2, system_cost)
    levels = np.linspace(z.min(), z.max(), 20)   
    plotz  = plot_contour(x,y,z,levels,var_dimension)
    return plotz

# --------- battery plot
    
def battery_TP(xaxis, mean_residence_time, max_residence_time, max_headroom, battery_output):
    y1 = np.squeeze(avg_series(mean_residence_time, 1, 1,8640,24,1))
    y2 = np.squeeze(avg_series(max_residence_time,  1, 1,8640,24,1))
    y3 = np.squeeze(avg_series(max_headroom,        1, 1,8640,24,1))
    
    fig = plt.figure()
    fig.subplots_adjust(top=1, left=0.0, right=1, hspace=1.0, wspace=0.35)

    ax1 = plt.subplot2grid((3,1),(0,0),rowspan=1, colspan=1)
    ax1v = ax1.twinx()
    ln1 = ax1.stackplot(xaxis, y1, colors ='g', baseline = 'zero', alpha=0.5, labels=['Mean residence time'])
    ln2 = ax1.plot(xaxis,      y2, c = 'green', alpha=0.5,    label='Max energy storage (kWh/kW)')
    ln3 = ax1v.plot(xaxis,     y3, c = 'red',   alpha=0.5,    label='Max headroom ')
    lns = ln1+ln2+ln3
    labs = [l.get_label() for l in lns]
    leg = ax1.legend(lns, labs, loc='center left', ncol=1, 
                     bbox_to_anchor=(1.07, 0.5), prop={'size': 5})
    leg.get_frame().set_alpha(0.4)
    ax1.set_title('(Left) battery storage required to satisfy demand at each hour\n'+\
                  '(Right) maximum headroom required to satisfy demand at each hour',
                  fontsize = 10)
    ax1.set_xlabel('time step (day)')
    plt.setp(ax1.get_xticklabels(), size=7)
    plt.setp(ax1.get_yticklabels(), size=7, color='green')
    plt.setp(ax1v.get_yticklabels(), size=7, color='red')
    
    array_to_draw = y1
    ax2 = plt.subplot2grid((3,1),(2,0),rowspan=1, colspan=1)
    weights = np.ones_like(array_to_draw)/float(len(array_to_draw))
    ax2.hist(array_to_draw, 50, weights=weights, label = 'Frequency distribution of\nmean residence time')
    leg = ax2.legend(loc='center left', ncol=1, 
                     bbox_to_anchor=(1.07, 0.5), prop={'size': 5})
    ax2.set_title('Frequency of battery storage for demand at a particular hour',
                  fontsize = 10)
    ax2.set_xlabel('Battery storage (kWh/kW)')
    plt.setp(ax2.get_xticklabels(), size=7)
    plt.setp(ax2.get_yticklabels(), size=7)
    
    ax3 = plt.subplot2grid((3,1),(1,0),rowspan=1, colspan=1)
    ax3.stackplot(xaxis[::4], battery_output[0][::4], labels = ['Battery discharge'])
    ax3.stackplot(xaxis[::4], battery_output[1][::4]*(-1), labels = ['Battery charge'])
    ax3.plot(xaxis[::4], battery_output[1][::4]*(1.-battery_output[2])*(-1), c='k', label = 'Energy loss from charging')
    leg = ax3.legend(loc='center left', ncol=1, 
                     bbox_to_anchor=(1.07, 0.5), prop={'size': 5})
    ax3.set_title('Battery charge and discharge',
                  fontsize = 10)
    ax3.set_xlabel('time step (day)')
    #plt.show()
    #plt.savefig(case_name+'_Battery.pdf',dpi=200,bbox_inches='tight',transparent=True)
    return fig
    plt.close(fig)
    
    
def battery_calculation(
        num_time_periods,
        dispatch_to_storage,
        dispatch_from_storage,
        energy_storage,
        storage_charging_efficiency
        ):
    start_point = 0.
    for idx in range(num_time_periods):
        if energy_storage[idx] == 0:
            start_point = idx

    lifo_stack = []
    tmp = 0.
    
    for idx in range(num_time_periods-start_point):
        idx = idx + start_point
        tmp = tmp + dispatch_to_storage[idx] - dispatch_from_storage[idx]
              
        if dispatch_to_storage[idx] > 0:  # push on stack (with time moved up 1 cycle)
            lifo_stack.append([idx-num_time_periods,dispatch_to_storage[idx]*storage_charging_efficiency ])
        if dispatch_from_storage[idx] > 0:
            dispatch_remaining = dispatch_from_storage[idx]
            while dispatch_remaining > 0:
                #print len(lifo_stack),dispatch_from_storage[idx],dispatch_remaining
                if len(lifo_stack) != 0:
                    top_of_stack = lifo_stack.pop()
                    if top_of_stack[1] > dispatch_remaining:
                        # partial removal
                        new_top = np.copy(top_of_stack)
                        new_top[1] = new_top[1] - dispatch_remaining
                        lifo_stack.append(new_top)
                        dispatch_remaining = 0
                    else:
                        dispatch_remaining = dispatch_remaining - top_of_stack[1]
                else:
                    dispatch_remaining = 0 # stop while loop if stack is empty
    # Now we have the stack as an initial condition and can do it for real
    max_headroom = np.zeros(num_time_periods)
    mean_residence_time = np.zeros(num_time_periods)
    max_residence_time = np.zeros(num_time_periods)
    
    for idx in range(num_time_periods):
        max_head = 0
        mean_res = 0
        max_res = 0
        if dispatch_to_storage[idx] > 0:  # push on stack
            lifo_stack.append([idx,dispatch_to_storage[idx]*storage_charging_efficiency ])
        if dispatch_from_storage[idx] > 0:
            dispatch_remaining = dispatch_from_storage[idx]
            accum_time = 0
            while dispatch_remaining > 0:
                if lifo_stack != []:
                    top_of_stack = lifo_stack.pop()
                    if top_of_stack[1] > dispatch_remaining:
                        # partial removal
                        accum_time = accum_time + dispatch_remaining * (idx - top_of_stack[0])
                        new_top = np.copy(top_of_stack)
                        new_top[1] = new_top[1] - dispatch_remaining
                        lifo_stack.append(new_top) # put back the remaining power at the old time
                        dispatch_remaining = 0
                    else: 
                        # full removal of top of stack
                        accum_time = accum_time + top_of_stack[1] * (idx - top_of_stack[0])
                        dispatch_remaining = dispatch_remaining - top_of_stack[1]
                else:
                    dispatch_remaining = 0 # stop while loop if stack is empty
            mean_res = accum_time / dispatch_from_storage[idx]
            max_res = idx - top_of_stack[0]
            # maximum headroom needed is the max of the storage between idx and top_of_stack[0]
            #    minus the amount of storage at time idx + 1
            energy_vec = np.concatenate([energy_storage,energy_storage,energy_storage])
            max_head = np.max(energy_vec[int(top_of_stack[0]+num_time_periods):int(idx + 1+num_time_periods)]) - energy_vec[int(idx + 1 + num_time_periods)]   # dl-->could be negative?
        max_headroom[idx] = max_head
        mean_residence_time[idx] = mean_res
        max_residence_time[idx] = max_res
    return max_headroom,mean_residence_time,max_residence_time

def cycles_per_year(dispatch_from_storage, max_headroom):
    hrt = np.transpose(np.array((max_headroom,dispatch_from_storage)))
    hrt1 = hrt[hrt[:,0].argsort()]
    hrt0_unique = np.sort(np.unique(hrt1[:,0])).tolist()
    output = []
    for headroom in hrt0_unique:
        subset = hrt1[hrt1[:,0] == headroom]
        record = [
                headroom,
                np.sum(subset[:,1]), # dispatch
                0., # margingal increase in headroom
                0., # cumulative dispatch
                0., #  increase in headroom / increase in dispatch
                0. #  increase in dispatch / increase in headroom
                ]
        output.append(record)
    output = np.array(output)
    output[1:,2]=output[1:,0]-output[:-1,0] # marginal increase in headroom
    output[:,3] = np.cumsum(output[:,1]) # take cumulative sum 
    output[1:,4] = output[1:,2]/output[1:,1] # increase in headroom per kWh delivered
    output[1:,5] = output[1:,1]/output[1:,2] # increase in kWh delivered per increase in headroom
    
    headroom_table = output
    return headroom_table

def battery_simpleline(xaxis, y1, y2, co):
    fig = plt.figure()
    ax1 = fig.add_subplot(111)    
    ax1.stackplot(xaxis[::4], y1[::4])
    ax1.stackplot(xaxis[::4], y2[::4]*(-1))
    ax1.plot(xaxis[::4], y2[::4]*(1.-co)*(-1), c='k')
    plt.show()
    plt.clf()

def battery_plot(res,
                 num_case,
                 case_name,
                 multipanels,
                 *select_case):
    
    # --- multi case plot
    num_time_periods = len(res[0]['demand'])
    
    find_case_idx = False
    if select_case:
        var1 = get_multicases_results(res, num_case , select_case[0][0])
        var2 = get_multicases_results(res, num_case , select_case[0][1])
        for idx in range(num_case):
            if var1[idx] == select_case[1][0] and var2[idx] == select_case[1][1]:
                find_case_idx = True
                case_idx = idx
                break
        if find_case_idx: 
            print 'Find case index:', case_idx
        else:
            print 'Error: no such case'
            sys.exit(0)
    if find_case_idx == False:
        case_idx = 0
    
    dispatch_to_storage         = get_multicases_results(res, num_case, 'dispatch_to_storage')[case_idx]
    dispatch_from_storage       = get_multicases_results(res, num_case, 'dispatch_from_storage')[case_idx]
    energy_storage              = get_multicases_results(res, num_case, 'energy_storage')[case_idx]
    storage_charging_efficiency = get_multicases_results(res, num_case, 'storage_charging_efficiency')[case_idx]
    max_headroom, mean_residence_time, max_residence_time = battery_calculation(num_time_periods,
                                                                                dispatch_to_storage,
                                                                                dispatch_from_storage,
                                                                                energy_storage,
                                                                                storage_charging_efficiency)
    aa = dispatch_from_storage
    bb = dispatch_to_storage
    aaa = np.squeeze(avg_series(aa, 1, 1,8640,24,1))
    bbb = np.squeeze(avg_series(bb, 1, 1,8640,24,1))
    ccc = storage_charging_efficiency
    battery_output = [aaa, bbb, ccc]
    
    xaxis = np.arange(360)+1
    plotk = battery_TP(xaxis,mean_residence_time,max_residence_time,max_headroom,battery_output)
    
    return plotk

def post_process(file_info):
    file_path = file_info['output_folder']+'/'
    scenario_name = file_info['base_case_switch']+'_'+file_info['case_switch']+'.pickle'
    
    verbose = True
    multipanel = True
    pp = PdfPages(file_path + scenario_name[:-7]+'_BOOK.pdf')
    file_list = os.listdir(file_path)
    
    for file in file_list:
        case_name = file
        if scenario_name == 'all' or case_name == scenario_name:
            print 'deal with case:', case_name
        
            file_info, time_series, assumption_list, result_list = unpickle_raw_results(
                            file_path + case_name,
                            verbose
                            )
            res = prepare_scalar_variables(
                    file_info,
                    time_series,
                    assumption_list,
                    result_list,
                    verbose
                    )
            cost_list, var_list = get_dimension_info(assumption_list)
            
            num_case = len(res)
            num_var_list = len(var_list) 
            
            dimension = 0
            var_dimension = []    
            for idx in range(num_var_list):
                if cost_list[var_list[idx]].size > 1:
                    dimension = dimension+1
                    var_dimension.append( var_list[idx] )
            if dimension == 0:
                print "set at least one dimension change"
                sys.exit()
            elif dimension == 1 or dimension ==2:
                if dimension ==1:
                    print "variation list:", var_dimension[0]
                    plotx = stack_plot1(res, num_case, case_name,multipanel, var_dimension)
                    pp.savefig(plotx,dpi=200,bbox_inches='tight',transparent=True)
                    for idx in range( len(cost_list[var_dimension[0]]) ):
                        select_case1 = [var_dimension[0], var_dimension[0]]
                        select_case2 = [cost_list[var_dimension[0]][idx], cost_list[var_dimension[0]][idx]]
                        ploty = stack_plot2(res, num_case, case_name,multipanel, var_dimension, select_case1, select_case2)
                        plotk = battery_plot(res,num_case,case_name, multipanel, select_case1, select_case2)
                        pp.savefig(ploty,dpi=200,bbox_inches='tight',transparent=True)
                        pp.savefig(plotk,dpi=200,bbox_inches='tight',transparent=True)
                else:
                    print "variation list 1:", var_dimension[0]
                    print "variation list 2:", var_dimension[1]
                    plotz = contour_plot(res,num_case, case_name, var_dimension)
                    pp.savefig(plotz,dpi=200,bbox_inches='tight',transparent=True)
                    for idx_1 in range( len(cost_list[var_dimension[0]])):
                        subset_res = {}
                        num_idx = 0
                        for idx_2 in range(num_case):
                            if res[idx_2][var_dimension[0]] == cost_list[var_dimension[0]][idx_1]:
                                subset_res[num_idx] = res[idx_2]
                                num_idx = num_idx + 1
                        plotx = stack_plot1(subset_res, num_idx, case_name, multipanel, [var_dimension[1]])
                        pp.savefig(plotx,dpi=200,bbox_inches='tight',transparent=True)
                        for idx_3 in range( len(cost_list[var_dimension[1]]) ):
                            select_case1 = [var_dimension[0], var_dimension[1]]
                            select_case2 = [cost_list[var_dimension[0]][idx_1], cost_list[var_dimension[1]][idx_3]]
                            ploty = stack_plot2(res, num_case, case_name,multipanel, var_dimension, select_case1, select_case2)
                            plotk = battery_plot(res,num_case,case_name, multipanel, select_case1, select_case2)
                            pp.savefig(ploty,dpi=200,bbox_inches='tight',transparent=True)
                            pp.savefig(plotk,dpi=200,bbox_inches='tight',transparent=True)
                    for idx_1 in range( len(cost_list[var_dimension[1]])):
                        subset_res = {}
                        num_idx = 0
                        for idx_2 in range(num_case):
                            if res[idx_2][var_dimension[1]] == cost_list[var_dimension[1]][idx_1]:
                                subset_res[num_idx] = res[idx_2]
                                num_idx = num_idx + 1
                        plotx = stack_plot1(subset_res, num_idx, case_name, multipanel, [var_dimension[0]])
                        pp.savefig(plotx,dpi=200,bbox_inches='tight',transparent=True)
                        for idx_3 in range( len(cost_list[var_dimension[0]]) ):
                            select_case1 = [var_dimension[0], var_dimension[1]]
                            select_case2 = [cost_list[var_dimension[0]][idx_3], cost_list[var_dimension[1]][idx_1]]
                            ploty = stack_plot2(res, num_case, case_name,multipanel, var_dimension, select_case1, select_case2)
                            plotk = battery_plot(res,num_case,case_name, multipanel, select_case1, select_case2)
                            pp.savefig(ploty,dpi=200,bbox_inches='tight',transparent=True)
                            pp.savefig(plotk,dpi=200,bbox_inches='tight',transparent=True)
                        """    
                    for idx_1 in range( len(cost_list[var_dimension[0]]) ):
                        for idx_2 in range( len(cost_list[var_dimension[1]]) ):
                            select_case1 = [var_dimension[0], var_dimension[1]]
                            select_case2 = [cost_list[var_dimension[0]][idx_1], cost_list[var_dimension[1]][idx_2]]
                            ploty = stack_plot2(res, num_case, case_name,multipanel, var_dimension, select_case1, select_case2)
                            plotk = battery_plot(res,num_case,case_name, multipanel, select_case1, select_case2)
                            pp.savefig(ploty,dpi=200,bbox_inches='tight',transparent=True)
                            pp.savefig(plotk,dpi=200,bbox_inches='tight',transparent=True)
                        """
            else:
                print "not support larger than 2 dimensions yet"
                sys.exit()
    pp.close()

#===============================================================================
#================================================== EXECUTION SECTION ==========
#===============================================================================
    

#file_info = {'output_folder':'/Users/leiduan/Desktop/File/phd/phd_7/CIS_work/Energy_optimize_model/WORK/Results/idealized_nuclear_solar_wind_bat 20180412_104058',
#             'base_case_switch':'idealized',
#             'case_switch':'nuclear_solar_wind_bat'}

#file_info = {'output_folder':'/Users/leiduan/Desktop/File/phd/phd_7/CIS_work/Energy_optimize_model/WORK/Results/Mengyao_data/one_year_simulations',
#             'base_case_switch':'idealized',
#             'case_switch':'ng_flex_nuc'}
#post_process(file_info)