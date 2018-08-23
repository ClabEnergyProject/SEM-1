# -*- coding: utf-8 -*-
"""

Takes output from the simple energy model and produces time series of hourly
cost of delivering electricity.

Created on Wed Aug 22 17:50:11 2018

@author: kcaldeira
"""
import numpy as np

#%%
#  Takes a capacity cost (fixed cost) and dispatch cost (variable cost) and
#  a time series of generation, and returns the hourly cost under the assumption
#  that the fixed costs are distributed across the generation that needed that
#  amount of capacity or less.
#
#  For example, let's say you had 5 hours of operation, with dispatch of
#     dispatch = [ 0, 1, 1, 1, 2 ]
#  And a capacity_cost and dispatch_cost of 1 $/kWh
#  The dispatch related costs would be [0, 1, 1, 1, 2]
#
#  But with 2 kW of capacity for 5 hours, you needed 1 kW of capacity for 4 hours, adding
#  5/4 = 1.25 $/hr to the cost of those hours. You needed an additional 1 kW
#  of capacity, adding 5/1 = 5 $/hr for that time so the capacity related costs
#  would be [0, 1.25, 1.25, 1.25, 6.25] for a grand total of
#  cost_per_hour = [0 , 2.25, 2.25, 2.25, 8.25 ] as the cost per hour.
#  This must be divided by kW to get cost per kWh
#  cost_per_kWh = [0, 2.25, 2.25, 2.25, 4.125 ]
#
def cost_model_dispatchable(capacity_cost_in, dispatch_cost_in, dispatch_in):
    capacity_cost = float(capacity_cost_in) # avoid integer arithmatic
    dispatch_cost = float(dispatch_cost_in)
    dispatch = np.array(dispatch_in)
    num_hours = len(dispatch)
    
    order = np.argsort(dispatch)[::-1] # indices of dispatch in descending order
    unsort_order = np.argsort(order)
    
    # The highest amount of use is used for 1 hour, the second highest is needed for 2 hours, etc
    needed_hours = 1. + np.arange(num_hours)
    
    incr_capacity = dispatch[order[:-1]] - dispatch[order[1:]]
    incr_capacity= np.append(incr_capacity,dispatch[order[-1]])
    
    incr_capacity_div_hours_used = incr_capacity / needed_hours
    
    cum_incr_capacity_sorted= np.cumsum(incr_capacity_div_hours_used[::-1])[::-1]
    
    cum_incr_capacity = cum_incr_capacity_sorted[unsort_order]
    
    cost_per_hour = dispatch_cost * dispatch + capacity_cost * num_hours * cum_incr_capacity
    cost_per_kWh = cost_per_hour / dispatch
    
    return cost_per_hour, cost_per_kWh # cost of generation for each hour


#%%
#  Takes a capacity cost (fixed cost) and dispatch cost (variable cost) and
#  a time series of generation, and returns the hourly cost under the assumption
#  that the fixed costs are distributed across the generation that needed that
#  amount of capacity or less.
#
#  For example, let's say you had 5 hours of operation, with dispatch of
#     dispatch = [ 0, 1, 2, 1, 1 ]
#  But let's say that the wind power available per hour was:
#     capacity = [ 0, 1, 2, 0.5, 1]
#  where this is the capacity per unit capacity installed.
#
#  Then the amount of capacity needed for each hour is these two divide 
#       capacity_needed = [0, 1, 1, 2, 1]
#
#  And a capacity_cost and dispatch_cost of 1 $/kWh
#  The dispatch related costs would be [0, 1, 2, 1, 1]
#
#  But with 2 kW of capacity for 5 hours, you needed 1 kW of capacity for 4 hours, adding
#  5/4 = 1.25 $/hr to the cost of those hours. You needed an additional 1 kW
#  of capacity, adding 5/1 = 5 $/hr for that time so the capacity related costs
#  would be [0, 1.25, 1.25, 6.25, 1.25] for a grand total of
#  cost_per_hour = [0 , 2.25, 3.25, 7.25, 2.25 ] as the cost per hour.
#  This must be divided by kW to get cost per kWh
#  cost_per_kWh = [0, 2.25, 1.125, 7.25, 2.25 ]
#
def cost_model_intermittent(capacity_cost_in, dispatch_cost_in, dispatch_in, capacity_in):
    capacity_cost = float(capacity_cost_in) # avoid integer arithmatic
    dispatch_cost = float(dispatch_cost_in)
    dispatch = np.array(dispatch_in, dtype=float) # dispatch time series
    capacity = np.array(capacity_in, dtype=float) # hourly generation capacity per unit capacity installed
    capacity_needed = np.divide(dispatch, capacity, out = np.zeros_like(dispatch), where=capacity!=0)
    
    num_hours = len(dispatch)
    
    order = np.argsort(capacity_needed)[::-1] # indices of dispatch in descending order
    unsort_order = np.argsort(order)
    
    # The highest amount of use is used for 1 hour, the second highest is needed for 2 hours, etc
    needed_hours = 1. + np.arange(num_hours)
    
    incr_capacity = capacity_needed[order[:-1]] - capacity_needed[order[1:]]
    incr_capacity= np.append(incr_capacity,capacity_needed[order[-1]])
    
    incr_capacity_div_hours_used = incr_capacity / needed_hours
    
    cum_incr_capacity_sorted= np.cumsum(incr_capacity_div_hours_used[::-1])[::-1]
    
    cum_incr_capacity = cum_incr_capacity_sorted[unsort_order]
    
    cost_per_hour = dispatch_cost * dispatch + capacity_cost * num_hours * cum_incr_capacity
    cost_per_kWh = cost_per_hour / dispatch
    
    return cost_per_hour, cost_per_kWh # cost of generation for each hour
      