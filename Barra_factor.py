# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

########SIZE（市值因子）：公司股票总市值的自然对数
mv = pd.read_csv(r'E:\PHBS\QTA\data0\freeMV.csv')
mv.replace(0, np.nan, inplace=True)
##查找数据中是否有字符串
##print([col for col, dt in mv.dtypes.items() if dt == object])
mv.iloc[:,1:] = mv.iloc[:,1:].apply(np.log)

########MOMENTUM(动量因子)
'''
rstr=sum_{t=L}^{T+L}w_tln(1+r_t)-sum_{t=L}^{T+L}w_tln(1+r_ft)
其中T=504,L=21,r_ft是无风险收益，w_i是指数加权权重，半衰期为126
指数加权权重算法：
w_i=(1-\alpha)^i*\alpha (i<t)
w_i=(1-\alpha)^i (i=t)
\alpha=1-e^{ln0.5/h},h是半衰期
'''

##计算收益率
adjPrice = pd.read_csv(r'E:\PHBS\QTA\data0\adj_price.csv')
status = pd.read_csv(r'E:\PHBS\QTA\data0\trading_status01.csv')
adjPrice.iloc[:, 1:] = adjPrice.iloc[:, 1:].mul(status)###去除无效数据
adjPrice.replace(0, np.nan, inplace=True)

adjPriceDiff = adjPrice.iloc[:, 1:].apply(np.diff)
rate = adjPriceDiff.div(adjPrice.iloc[:-1, 1:])
rate = rate.reindex(columns=list(adjPrice.columns), fill_value=1)
rate.iloc[:, 0] = list(adjPrice.iloc[1:, 0])

##计算指数加权权重
alpha = 1-np.exp(np.log(0.5)/126)
weight = [0]*504
for i in range(0, 503):
    weight[i]=np.power((1-alpha), i)*alpha
weight[503] = np.power((1-alpha), 503)

##计算动量因子
lnrate = rate.iloc[:, 1:].add(1)
lnrate = lnrate.apply(np.log)
lnrate = lnrate.iloc[::-1]

rstr=lnrate.rolling(504, min_periods=504).apply(func=lambda x: x.mul(weight).sum())
rstr = rstr.iloc[::-1]
rstr = rstr.iloc[:715, :]
rstr = rstr.reindex(columns=list(adjPrice.columns), fill_value=1)
rstr.iloc[:694, 0] = list(adjPrice.iloc[-694:, 0])
rstr.to_csv(r'E:\PHBS\QTA\data0\rstr.csv', index=False)