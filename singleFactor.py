# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from datetime import datetime

# MAD:中位数去极值
#####test data#####
class testData:
    def __init__(self, factors):
        self.factors = ['rate', factors]
        ###必要的收益率和过滤表
        self.adjPrice = pd.read_csv(r'E:\PHBS\QTA\data0\adj_price.csv')
        self.status = pd.read_csv(r'E:\PHBS\QTA\data0\trading_status01.csv')
        self.rate = self.adjPrice
        self.rate.iloc[:, 1:] = self.rate.iloc[:, 1:].pct_change()
        self.dataDict = self.standarlize()

    ###MAD去极值
    def extreme_MAD(self, dt, n):
        dt1 = dt.iloc[:, 1:].T
        median = dt1.quantile(0.5)  # 找出中位数
        new_median = (abs((dt1 - median)).quantile(0.5))  # 偏差值的中位数
        dt1_up = median + n * new_median  # 上限
        dt1_down = median - n * new_median  # 下限
        dt.iloc[:, 1:] = dt1.clip(dt1_down, dt1_up, axis=1).T  # 超出上下限的值，赋值为上下限
        return dt

    ###数据处理终版
    def standarlize(self):
        dataDict = {'rate': self.rate}
        for i in self.factors:
            if i == 'rate':
                dataDict[i].iloc[:, 1:] = dataDict[i].iloc[:, 1:].mul(self.status.iloc[:, 1:])
                dataDict[i].replace(0, np.nan, inplace=True)
                dataDict[i] = self.extreme_MAD(dataDict[i], 5)
            else:
                dataDict[i] = pd.read_csv('E:\PHBS\QTA\data0' + '\\' + i + '.csv')
                dataDict[i].iloc[:, 1:] = dataDict[i].iloc[:, 1:].mul(self.status.iloc[:, 1:])
                dataDict[i].replace(0, np.nan, inplace=True)
                dataDict[i] = self.extreme_MAD(dataDict[i], 5)

        return dataDict

data = testData('rstr').dataDict


class singleFactor:
    def __init__(self, beginTime, endTime, factor, dataDict, stock='all'):
        self.begTime = datetime.date(datetime.strptime(beginTime, '%Y/%m/%d'))
        self.endTime = datetime.date(datetime.strptime(endTime, '%Y/%m/%d'))
        self.factor = factor
        self.stock = stock
        self.dataDict = dataDict
        self.data = self.myMerge()###所需因子集合，双索引

    #将指定的因子按照时间范围，股票范围切片，并将时间化为datatime，最后将dataframe化为双索引，column名为变量名
    def catchData(self, a):
        result = self.dataDict[a]
        if self.stock != 'all':
            result = result[self.stock]
        result = result.rename(columns={result.columns[0]: 'datetime'})
        for i in range(0, len(result)):
            result.loc[i, 'datetime'] = datetime.strptime(result.loc[i, 'datetime'], '%Y/%m/%d')
            result.loc[i, 'datetime'] = datetime.date(result.loc[i, 'datetime'])
        result = result.set_index(result.columns[0])
        result = result.loc[(result.index >= self.begTime) & (result.index <= self.endTime)]
        result = result.stack().to_frame()
        result.columns = [a]
        return result

    ###将所需的全部因子合并在一个dataframe里
    def myMerge(self):
        a = self.catchData('rate')
        b = self.catchData(self.factor)
        #c = self.catchData('freeMV')
        #d = self.catchData('industry')
        result = pd.merge(a, b, left_index=True, right_index=True)
        #result = pd.merge(result, c, left_index=True, right_index=True)
        #result = pd.merge(result, d, left_index=True, right_index=True)
        result.index.names = ['datetime', 'stock']
        return result

    ###分层回测函数
    def layeredBacktest(self, groupNum, weight='equal', industryNeutral=False, secondFactor = False, plot = True,):
        quantile = self.data[self.factor].groupby(level='datetime').quantile(np.arange(0, 1+1/groupNum, 1/groupNum))
        group = list(range(1, groupNum+1))
        dateTotal = self.data.reset_index()['datetime'].unique()
        for i in dateTotal:
            a = pd.cut(self.data.loc[i, self.factor], bins=list(quantile[i]), labels=group, include_lowest=True)
            self.data.loc[i, 'group'] = list(a)
        if industryNeutral == False:
            if weight == 'equal':
                rateGroup = self.data.groupby(['datetime', 'group'])['rate'].mean()
            # elif weight == "MV":
            #     industrySum = self.data.groupby(['datetime', 'group'])['industry'].sum()
            #     for i in dateTotal:
            #         a = pd.cut(self.data.loc[i, self.factor], bins=list(quantile[i]), labels=group, include_lowest=True)
            #         self.data.loc[i, 'group'] = list(a)
            #     self.data['weight'] = self.data.groupby(['datetime', 'group'])['industry'].div(industrySum)
            #     self.data['rateWeighted'] = self.data.groupby(['datetime', 'group'])['rate'].mul(self.data.groupby(['datetime', 'group'])['industry'])
            #     rateGroup = self.data.groupby(['datetime', 'group'])['rateWeighted'].mean()

        rateGroup = rateGroup.unstack()
        rateGroup = -rateGroup.cumsum()
        rateGroup.plot()
        return rateGroup

test = singleFactor('2017/3/1','2019/12/31', 'rstr', data)

