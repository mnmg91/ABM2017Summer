#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 13 00:01:26 2017

@author: limengchu
"""
import random
import numpy as np

'''This module provides the simulation algorithms to capture different 
   behaviour rules in the evolutionary choice model. The basic structure includes 
   Preferential Attachment (PA) principle, i.e. replicating one of the 
   decisions previously made by other agents according to proportion of people 
   chose it, and innovation mechanism. 

    An overview of the functions:
    ----------------------------
    sim_random_inn:  Agents choose either by PA principle with memory parameter 
                    or innovation. When choosing to innovate, they will first 
                    add product to the current pool (num_k1), until it reaches 
                    the maximum number of products (num_p). Then they choose 
                    randomly among total number of products.

    sim_revive_inn:  Agents choose either by PA principle with memory parameter 
                    ‘m’ or innovation. When choosing to innovate, they randomly
                    choose among the products that were not available in the 
                    previous m steps. 
    --------------------------------------------------------------------------   
    
    Shared Parameters:
    -----------------
       num_people: list
                   A list of number of people enter the system at each time step. 
                   Could be generated by functions in Agent_growth.py. 
           mem   : integer
                   Memory parameter determines the number of steps agents will 
                   look back when copying from others and innovating.
           inn   : float
                   Innovation parameter determines the probability with which 
                   an agent violates the PA principle and choose to innovate instead.
          num_p  : integer
                   The total number of products available at the end of the process.
        wholedist: bool
                   The output of the functions will be determined by this parameter.
                   If True, functions will return the whole [num_p by len(num_people)] 
                   matrix. It provides all the information for each product at each time step.
                   If False, functions will return the Final distribution calculated by 
                   summing along all time steps. The default value if False. 
    -----------------------------------------------------------------------------------
    The following commands should be helpful to pretty-print the result in numpy arrays
    
    np.set_printoptions(threshold = np.inf)  to print the full array instead of truncated representation   
    np.set_printoptions(suppress=True)       to print without scientific notation

'''
def sim_random_inn(num_people, mem, inn, num_p, num_k1, wholedist = False):
    '''Specific parameters:
       -------------------
        num_k1: interger
                The number of products available at first time step. It might be 
                increased to the num_p through the innovation process. 
                Need to be positive.
    '''
    # at first time step, agents choose randomly from the available products 
    tau = len(num_people)
    Prop_choice = np.zeros((num_p,tau))
    S = [random.choice(range(num_k1)) for i in range(num_people[0])]
    Prop_choice[:,0] = [S.count(i) for i in range(num_p)]
    
    # from t=1 till the end of the simulation, agents' decision is governed by behaviour rule
    for t in range(1,tau):
        weight_samp = Prop_choice[:,range(max(0,(t-mem)),t)].sum(axis=1)
        total = sum(weight_samp)
        inn_pool = range(num_p)
        if len(inn_pool) > 0:
            # check how many agents innovate 
            innvec=[random.random()<inn for i in range(num_people[t])]
            k = sum(innvec)
            inn_group = np.array([0]*num_p)
            if k>0:
                # check if the increment of products by innovation will be larger than num_p
                if num_k1 == num_p:
                    SS = [random.choice(inn_pool) for i in range(k)]
                    inn_group = np.array([SS.count(i) for i in range(num_p)])
                elif num_p >= num_k1+k:
                    for i in range(num_k1,num_k1+k):
                        inn_group[i]=1 
                    num_k1 = num_k1+k
                else:
                    inn_group[num_k1:]=1
                    excessrd = [random.choice(inn_pool) for i in range(num_k1+k-num_p)]
                    excessrd = np.array([excessrd.count(i) for i in range(num_p)])
                    num_k1 = num_p
                    inn_group = inn_group+excessrd  
            # Agents who do not innovate form the conf_group
            Sam_noinn = np.random.choice(num_p,num_people[t]-k,p=weight_samp/float(total))
            conf_group = np.array([Sam_noinn.tolist().count(i) for i in range(num_p)])
            Prop_choice[:,t] = conf_group + inn_group
    Finaldis = Prop_choice.sum(axis=1)
    return Prop_choice if wholedist == True else Finaldis
    
def sim_revive_inn(num_people,mem,inn,num_p,num_k1 = None, wholedist = False):
    tau = len(num_people)
    Prop_choice = np.zeros((num_p,tau))
    S = [random.choice(range(num_p)) for i in range(num_people[0])]
    Prop_choice[:,0] = [S.count(i) for i in range(num_p)]
    for t in range(1,tau):
        weight_samp = Prop_choice[:,range(max(0,(t-mem)),t)].sum(axis=1)
        total = sum(weight_samp)
        # check which prodcuted were not available in the previous mem steps
        inn_pool = [i for i in range(len(weight_samp)) if weight_samp[i] == 0]
        inn_group = np.zeros(num_p)
        k=0
        if inn == 0: #inn = 0 is separated because it was a bottleneck for the simulation
            inn_pool = []
        if len(inn_pool) > 0:
            innvec=[random.random()<inn for i in range(num_people[t])]
            k = sum(innvec)
            if k>0:
                SS = [random.choice(inn_pool) for i in range(k)]
                inn_group = np.array([SS.count(i) for i in range(num_p)])
            else:
                inn_group = np.zeros(num_p)
        # Agents who do not innovate form the conf_group
        Sam_notinn = np.random.choice(num_p,num_people[t]-k,p=weight_samp/float(total))
        conf_group = np.array([Sam_notinn.tolist().count(i) for i in range(num_p)])
        Prop_choice[:,t] = conf_group + inn_group
    Finaldis = Prop_choice.sum(axis=1)
    return Prop_choice if wholedist == True else Finaldis

