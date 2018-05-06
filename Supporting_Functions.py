# -*- coding: utf-8 -*-
"""
Created on Fri Dec 01 16:31:28 2017

@author: Fan
"""

import numpy as np

def func_time_conversion ( input_data, time_duration, type = 'mean'):
    
    N = input_data.size / time_duration
    output_data = np.arange(N)
    
    for ii in range(N):
        # print 'ii=', ii
        if (type == 'mean'):        
            output_data[ii] = np.mean(input_data[ii*time_duration : (ii+1)*time_duration])
        elif(type == 'min'):
            output_data[ii] = np.min(input_data[ii*time_duration : (ii+1)*time_duration])
        elif(type == 'max'):
            output_data[ii] = np.max(input_data[ii*time_duration : (ii+1)*time_duration])
            
    return output_data