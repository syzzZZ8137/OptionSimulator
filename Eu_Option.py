# -*- coding: utf-8 -*-
"""
Created on Wed May 23 13:32:06 2018

@author: Jax_GuoSen
"""

import pandas as pd
import numpy as np
from scipy.stats import norm
#from matplotlib import pyplot as plt


def BS_formula(S,K,T,r,sigma,q,Otype):
    
    d1 = (np.log(S/K)+(r-q+0.5*sigma**2)*T)/(sigma*np.sqrt(T))
    d2 = (np.log(S/K)+(r-q-0.5*sigma**2)*T)/(sigma*np.sqrt(T))
    
    if Otype == 'call':

        V = S*np.exp(-q*T)*norm.cdf(d1)-K*np.exp(-r*T)*norm.cdf(d2)
        
    elif Otype =='put':
        
        V =K*np.exp(-r*T)*norm.cdf(-d2)-S*np.exp(-q*T)*norm.cdf(-d1)

    else:
        pass
        
    return V



def cpt_delta(S,K,T,r,sigma,q,Otype):
    
    d1=(np.log(S/K)+(r-q+0.5*sigma**2)*T)/(sigma*np.sqrt(T))
    
    if Otype =='call':
        
        delta = norm.cdf(d1)
        
    elif Otype =='put':
        
        delta = norm.cdf(d1)-1
        
    else:
        pass
        
    return delta

def cpt_gamma(S,K,T,r,sigma,q):
    
    d1 = (np.log(S/K)+(r-q+0.5*sigma**2)*T)/(sigma*np.sqrt(T))

    gamma = 1/(S*np.sqrt(2*np.pi*(sigma**2)*T))*np.exp((-d1**2)/2)

    return gamma

def cpt_theta(S,r,sigma,K,T,status):
    
    d1 = (np.log(S/K)+(r+0.5*sigma**2)*T)/(sigma*np.sqrt(T))
    
    d2 = (np.log(S/K)+(r-0.5*sigma**2)*T)/(sigma*np.sqrt(T))

    c1 = -S*sigma/(2*np.sqrt(2*np.pi*T))*np.exp((-d1**2)/2)
    
    c2 = -r*K*np.exp(-r*T)*norm.cdf(d2)
    
    c3 = r*K*np.exp(-r*T)*norm.cdf(-d2)
    
    if status == '认购':
        
        theta = c1+c2
        
    else:
        
        theta = c1+c3
        
    return theta

def cpt_vega(S,r,sigma,K,T):
    
    d1 = (np.log(S/K)+(r+0.5*sigma**2)*T)/(sigma*np.sqrt(T))

    vega = np.sqrt(T)*S*np.exp((-d1**2)/2)/np.sqrt(2*np.pi)
    
    return vega


def cpt_rho(S,r,sigma,K,T,status):
    
    d2 = (np.log(S/K)+(r-0.5*sigma**2)*T)/(sigma*np.sqrt(T))

    if status =='认购':
        
        rho = K*T*np.exp(-r*T)*norm.cdf(d2)
        
    else:
        
        rho = -K*T*np.exp(-r*T)*norm.cdf(-d2)
        
    return rho

