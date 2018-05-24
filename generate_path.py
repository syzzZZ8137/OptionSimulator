# -*- coding: utf-8 -*-
"""
Created on Wed May 23 13:44:36 2018

@author: Jax_GuoSen
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def random_gen(N=100000,TStep=1000):
    
    z = np.random.randn(N,TStep)
    
    return z

def Ret_path_gen(r,sigma,q,T,random):
    Ret_path = np.ones((random.shape[0],random.shape[1]))
    
    z = random
    dt = T/random.shape[1]
    
    for i in range(random.shape[1]-1):
        Ret_path[:,i+1] = np.exp((r-q-0.5*sigma**2)*dt+sigma*np.sqrt(dt)*z[:,i])  #产生收益率序列
    
    return Ret_path


def S_path_gen(S0,ret):
    S_path = np.zeros((ret.shape[0],ret.shape[1]))
    S_path[:,0] = S0
    
    for i in range(ret.shape[1]-1):
        S_path[:,i+1] = S_path[:,i]*ret[:,i+1]     #产生股价序列

    return S_path


if __name__ == '__main__':
    
    S = 1800
    K = 1800
    
    price_date = pd.datetime(2018,7,1)        #期权报价日
    maturity_date = pd.datetime(2018,11,1)    #期权到期日
    T =  (maturity_date-price_date).days/365
    
    sigma = 0.18
    r = 0.01
    q = 0
    
    option_type = 'call'
    Nsamples = 5000
    Tsteps = 100
    
    random = random_gen(Nsamples,Tsteps)
    ret = Ret_path_gen(r,sigma,q,T,random)
    S_path = S_path_gen(S,ret)
    plt.plot(S_path[:,:].T,lw = 1.5) 