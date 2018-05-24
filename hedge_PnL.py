# -*- coding: utf-8 -*-
"""
Created on Thu May  3 15:53:19 2018

@author: Jax_GuoSen
"""

import pandas as pd
import numpy as np


def hedge_PNL_usage(data,multiplier,commis,threshold):
    
    data['期权头寸'] = -data['期权头寸']
    tmp = data['期权头寸'][0]
    data['期货头寸'] = 0
    for i in range(len(data)):
        if abs(data.iloc[i,2]-tmp)<threshold:
            data.iloc[i,3] = -tmp
        else:
            data.iloc[i,3] = -data.iloc[i,2]
            tmp = data.iloc[i,2]  #记录此时的持仓
    
    
    data['风险敞口'] = data['期权头寸']+data['期货头寸']
    
    data['交易(手)'] = data['期货头寸'].diff()
    data['交易(手)'].fillna(data['期货头寸'].iloc[0],inplace=True)  #补第一个na数据
    data['手续费'] = -abs(data['交易(手)'])*commis  #今交手*单位手续费
    
    #data['前夜盈亏'] = 0
    #data['当日盈亏'] = 0
    #data['前夜盈亏'] = (data['期货头寸']*multiplier*(data['交易价'].shift(-1)-data['结算价'])).shift(1)  #（今交-昨结）*昨手
    #data['前夜盈亏'].fillna(0,inplace=True)
    #data['当日盈亏'] = data['期货头寸']*multiplier*(data['结算价']-data['交易价'])  #（今结-今交）*今手
    #data['当日盈亏'].fillna(0,inplace=True)
    
    #data['当日总盈亏'] = data['手续费']+data['前夜盈亏']+data['当日盈亏']
    #data['累计总盈亏'] = np.cumsum(data['当日总盈亏'])
    
    data['成交量(手)'] = np.cumsum(abs(data['交易(手)']))
    data['持仓量(手)'] = np.cumsum(data['交易(手)'])
    
    PnL = sum(-data['交易(手)']*multiplier*data['交易价']) + sum(data['手续费'])  #手续费前面保存为负值，所以这里+
    
    return data,PnL





if __name__ == '__main__':
    '''
    Input
    输入的文件格式参照input_file
    '''
    path = 'D:\场外期权\EU_ASIAN\\'
    input_file = 'Input_hedgePNL.xlsx'
    output_file = 'Output_hedgePNL.xlsx'
    multiplier = 5  #合约乘数
    commis = 20 #每手手续费
    
    threshold = 5  #期权头寸与期货头寸相差5手以内，不调仓
    '''
    Usage
    '''
    data = pd.read_excel(path+input_file,index_col=0)
    res,PnL = hedge_PNL_usage(data,multiplier,commis,threshold)
    
    '''
    Output
    '''
    writer1 = pd.ExcelWriter(path+output_file)
    res.to_excel(writer1)
    writer1.close()
