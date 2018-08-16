# -*- coding: utf-8 -*-
"""
Created on Wed May 23 14:42:04 2018

@author: Jax_GuoSen
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import generate_path
import Eu_Option as Eu
import hedge_PnL

def Main_Eu(S,K,T,Dayfreq,max_Dayfreq,sigma,sigma_simupath,r,q,option_type,Nsamples,Tsteps,multiplier,commis,threshold,num):
    hedge_sig = []
    freq = int(max_Dayfreq/Dayfreq)
    for i in range(Tsteps):
        if np.mod(i,freq)==0:
            hedge_sig.append(True)
        else :
            hedge_sig.append(False)
        
    
    
    #分割Tsteps,要计算delta的点位，记为1，否则记为0。
    
    random = generate_path.random_gen(Nsamples,Tsteps)
    ret = generate_path.Ret_path_gen(r,sigma_simupath,q,T,random)
    S_path = generate_path.S_path_gen(S,ret)
    #plt.plot(S_path[:,:].T,lw = 1.5)
    
    Delta_path = np.zeros((S_path.shape[0],S_path.shape[1]))+100
    Delta_path1 = np.zeros((S_path.shape[0],S_path.shape[1]))+100
    Gamma_path = np.zeros((S_path.shape[0],S_path.shape[1]))+100
    Vega_path = np.zeros((S_path.shape[0],S_path.shape[1]))+100
    Theta_path =np.zeros((S_path.shape[0],S_path.shape[1]))+100
    Rho_path = np.zeros((S_path.shape[0],S_path.shape[1]))+100
    
    
    dt = T/(S_path.shape[1]-1)
    
    for i in range(S_path.shape[0]):
        ttm = T
        for j in range(S_path.shape[1]):
            if hedge_sig[j]:
                S = S_path[i,j]
                tmp_delta = tmp_gamma = tmp_vega = tmp_theta = tmp_rho = 0
                
                for ii in range(len(K)):
                    tmp_delta += Eu.cpt_delta(S,K[ii],ttm,r,sigma[ii],q,option_type[ii])*num[ii]*multiplier
                    tmp_gamma += Eu.cpt_gamma(S,K[ii],ttm,r,sigma[ii],q)*num[ii]*multiplier
                    tmp_vega += Eu.cpt_vega(S,r,sigma[ii],K[ii],ttm)*num[ii]*multiplier/100
                    tmp_theta += Eu.cpt_theta(S,r,sigma[ii],K[ii],ttm,option_type[ii])*num[ii]*multiplier/365
                    tmp_rho += Eu.cpt_rho(S,r,sigma[ii],K[ii],ttm,option_type[ii])*num[ii]*multiplier/100
                    
                if np.isnan(tmp_delta):
                    pass
                else:
                    tmp_delta1 = int(tmp_delta/multiplier)*multiplier
                    #tmp_gamma = int(tmp_gamma/multiplier)*multiplier
                    #tmp_vega = int(tmp_vega/multiplier)*multiplier
                    #tmp_theta = int(tmp_theta/multiplier)*multiplier
                    #tmp_rho = int(tmp_rho/multiplier)*multiplier
                    
                    
                Delta_path1[i,j] = tmp_delta1 #取整了
                Delta_path[i,j] = tmp_delta
                Gamma_path[i,j] = tmp_gamma
                Vega_path[i,j] = tmp_vega
                Theta_path[i,j] = tmp_theta
                Rho_path[i,j] = tmp_rho
                
            else:
                Delta_path[i,j] = tmp_delta
                Gamma_path[i,j] = tmp_gamma
                Vega_path[i,j] = tmp_vega
                Theta_path[i,j] = tmp_theta
                Rho_path[i,j] = tmp_rho
                
            ttm = ttm - dt
            print(i,j)
    
    
    stat = []
    for i in range(S_path.shape[0]):
        data = pd.DataFrame(S_path[i,:],columns=['交易价'])
        data['结算价'] = data['交易价']
        data['期权头寸'] = pd.DataFrame(Delta_path1[i,:])
        data['期权头寸'].fillna(0,inplace=True)
        data.loc[len(data)-1,'期权头寸'] = 0  #最后平仓
        data['期权头寸'] = data['期权头寸']
        data['期权头寸'] = data['期权头寸'].apply(lambda x:int(x))
        data,PnL = hedge_PnL.hedge_PNL_usage(data,multiplier,commis,threshold)
        stat.append([data.loc[len(data)-1,'成交量(手)'],PnL])
        print(i)
        
    stat = pd.DataFrame(stat,columns=['成交量(手)','PnL'])
    
    return stat,S_path,Delta_path,Gamma_path,Vega_path,Theta_path,Rho_path



if __name__ == '__main__':
    '''Input'''
    S = 492
    K = [492,467,442]
    sigma = [0.35,0.2,0.2]
    sigma_simupath = 0.3 #模拟未来路径时的波动率。
    r = 0.01
    q = 0
    option_type = ['put','put','put']
    price_date = pd.datetime(2018,7,27)        #期权报价日
    maturity_date = pd.datetime(2018,8,27)    #期权到期日
    multiplier = 100  #合约乘数
    commis = 20 #每手手续费
    threshold = 500  #期权头寸与期货头寸相差threshold以内，不调仓
    num = [200,-100,-40] #对应标的总手数
    Dayfreq = 1  #每天对冲几次，最好应被max_Dayfreq整除
    max_Dayfreq = 1 #每天产生的价格点，应大于Dayfreq ,i.e.与Tsteps有关。
    Nsamples = 500  #模拟样本数
    
    T =  ((maturity_date-price_date).days+1)/365
    Tsteps = (maturity_date-price_date).days*max_Dayfreq  #每天离散出max_Dayfreq个点
    
    '''Input'''
    
    '''调用'''
    V_price = []
    for i in range(len(K)):
        tmp = Eu.BS_formula(S,K[i],T,r,sigma[i],q,option_type[i])*num[i]*multiplier
        V_price.append(tmp)
        
    stat,S_path,Delta_path,Gamma_path,Vega_path,Theta_path,Rho_path = Main_Eu(S,K,T,Dayfreq,max_Dayfreq,sigma,sigma_simupath,r,q,option_type,Nsamples,Tsteps,multiplier,commis,threshold,num)
    
    stat['成交量(手)'].plot(kind='hist',grid=True,color='blue')
    stat['成交量(手)'].plot(kind='density',grid=True,color='blue')
    stat['PnL'].plot(kind='hist',grid=True,color='red')
    stat['PnL'].plot(kind='kde',grid=True,color='blue')
    plt.plot(S_path.T)
    print(stat.describe())
    print('期权费',V_price)
    print('净赚(期权费+对冲盈亏)',V_price+stat['PnL'].mean())
    
    Delta_path_hist = []
    Gamma_path_hist = []
    Vega_path_hist = []
    Theta_path_hist = []
    Rho_path_hist = []
    for i in range(len(Delta_path)):
        Delta_path_hist.extend(Delta_path[i,:].tolist())
        Gamma_path_hist.extend(Gamma_path[i,:].tolist())
        Vega_path_hist.extend(Vega_path[i,:].tolist())
        Theta_path_hist.extend(Theta_path[i,:].tolist())
        Rho_path_hist.extend(Rho_path[i,:].tolist())
        
    Delta_path_hist = pd.DataFrame(Delta_path_hist)
    Gamma_path_hist = pd.DataFrame(Gamma_path_hist)
    Vega_path_hist = pd.DataFrame(Vega_path_hist)
    Theta_path_hist = pd.DataFrame(Theta_path_hist)
    Rho_path_hist = pd.DataFrame(Rho_path_hist)
    
    Delta_path_hist.plot(kind='hist',grid=True,color='blue',title='Delta_path',legend=False)
    Gamma_path_hist.plot(kind='hist',grid=True,color='blue',title='Gamma_path',legend=False)
    Vega_path_hist.plot(kind='hist',grid=True,color='blue',title='Vega_path',legend=False)
    Theta_path_hist.plot(kind='hist',grid=True,color='blue',title='Theta_path',legend=False)
    Rho_path_hist.plot(kind='hist',grid=True,color='blue',title='Rho_path',legend=False)
    
        
        
