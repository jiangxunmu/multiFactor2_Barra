# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from datetime import datetime
from scipy import optimize

rate = pd.read_csv(r'E:\PHBS\QTA\data0\rate.csv')
industry = pd.read_csv(r'E:\PHBS\QTA\data0\\industry.csv',encoding='gb2312')
rstr = pd.read_csv(r'E:\PHBS\QTA\data0\rstr.csv')

def addDate(data):
    data = data.rename(columns={data.columns[0]: 'datetime'})
    for i in range(0, len(data)):
        data.loc[i, 'datetime'] = datetime.strptime(data.loc[i, 'datetime'], '%Y/%m/%d')
        data.loc[i, 'datetime'] = datetime.date(data.loc[i, 'datetime'])
        data.loc[i, 'year'] = data.loc[i, 'datetime'].year
        data.loc[i, 'day'] = data.loc[i, 'datetime'].day
        data.loc[i, 'month'] = data.loc[i, 'datetime'].month
    return data
rate = addDate(rate)
rstr = addDate(rstr)
rstrMonth = rstr.groupby(['year', 'month']).mean()
rstrMonth = rstrMonth.reset_index()

industry = addDate(industry)
industry = industry[list(rate.columns)]
a = []
for i in range(0, len(industry)):
    for j in list(industry.columns[1:3909]):
        if isinstance(industry.loc[i, j], str) and industry.loc[i, j] not in a:
            a.append(industry.loc[i, j])
industryName = a
industry.replace(a, range(0, len(a)), inplace=True)

index300 = pd.read_csv(r'E:\PHBS\QTA\data0\300.csv')
name_data = list(index300.columns)
for i in range(0, len(name_data)):
    name_data[i] = name_data[i].replace('XSHG', 'SH')
    name_data[i] = name_data[i].replace('XSHE', 'SZ')
index300.columns = name_data
index300 = addDate(index300)
columnsName = list(index300.columns[1:504])
columnsName.append('year')
columnsName.append('month')
index300 = index300[columnsName].groupby(['year', 'month']).mean()
index300 = index300.reset_index()
a=[]
for i in list(rstr.columns):
    if i not in list(index300.columns):
        a.append(i)
index300 = pd.concat([index300, pd.DataFrame(columns=a)])
#index300[a] = index300.iloc[49,300]
index300 = index300[list(industry.columns)]

mv = pd.read_csv(r'E:\PHBS\QTA\data0\freeMV.csv')
mv = mv.rename(columns={mv.columns[0]: 'datetime'})
for i in range(0, len(mv)):
    mv.loc[i, 'datetime'] = datetime.strptime(str(mv.loc[i, 'datetime']), '%Y%m%d')
    mv.loc[i, 'datetime'] = datetime.date(mv.loc[i, 'datetime'])
    mv.loc[i, 'year'] = mv.loc[i, 'datetime'].year
    mv.loc[i, 'day'] = mv.loc[i, 'datetime'].day
    mv.loc[i, 'month'] = mv.loc[i, 'datetime'].month
mv = mv[list(rate.columns)]

year = list(rstrMonth['year'])
month = list(rstrMonth['month'])
columns = list(rstrMonth.columns)[0:3845]
industry = industry.loc[(industry['year'].isin(year)) & (industry['month'].isin(month)), columns]
#####################################################################################################################]
rstrMonthT = rstrMonth.loc[(rstrMonth['year']==2018) & (rstrMonth['month']==2), columns]
mvT = mv.loc[(mv['year']==2018) & (mv['month']==2), columns]
industryT = industry.loc[(industry['year']==2018) & (industry['month']==2), columns]
index300T = index300.loc[(index300['year']==2018) & (index300['month']==2), columns]
indexStock = list(index300T.loc[: ,index300T.isin([1]).any()].columns)
w_d = mvT[indexStock]
w_d = w_d.div(list(w_d.sum(axis=1))*300,axis=1)
a=[]
for i in list(index300T.columns):
    if i not in list(w_d.columns):
        a.append(i)
w_d = pd.concat([w_d, pd.DataFrame(columns=a)])
w_d = w_d[list(index300T.columns)]

###目标函数###
f=list(rstrMonthT.iloc[0,2:].mul(-1))
f=[0 if np.isnan(i) else i for i in f]
###市值中性###
X=list(mvT.iloc[0,2:])
X=[0 if np.isnan(i) else i for i in X]
w_dList=list(w_d.iloc[0,2:])
w_dList=[0 if np.isnan(i) else i for i in w_dList]
w_dX=np.multiply(np.array(X), np.array(w_dList)).sum()
###行业中性###
industryList=[]
industryIndexList=[]
for i in range(0, len(industryName)):
    a=b=[0]*len(columns[2:])
    for j in range(2, len(columns)):
        if industryT.iloc[0,j] == i:
            a[j-2] = 1
            if index300T.iloc[0,j] == 1:
                b[j-2] = 1
    industryList.append(a)
    industryIndexList.append(b)
mvIndustryIndex=[]
for i in range(0, len(industryName)):
    result=np.multiply(np.array(industryIndexList[i]),np.array(X)).sum()
    mvIndustryIndex.append(result)
for j in range(0,len(industryList)):
    industryList[j]=list(np.multiply(np.array(industryList[j]),np.array(X)))
###加和为1###
e=[1]*len(columns[2:])
###权重上下界限
wDown=[0]*len(w_dList)
wUp=[None]*len(w_dList)
for j in range(0,len(w_dList)):
    if w_dList[j] != 0 and not np.isnan(w_dList[j]):
        wUp[j] = w_dList[j]+0.02
        wDown[j] = max(0, w_dList[j]-0.02)
    if np.isnan(wDown[j]):
        wDown[j] = 0
    if f[j] == 0:
        wUp[j]=0
###指数股不少于80%
indexPart=list(index300T.iloc[0,2:].mul(-1))
indexPart=[0 if np.isnan(i) else i for i in indexPart]
#####################
c=np.array(f)
A_ub=np.array([indexPart])
b_ub=np.array([-0.8])
A_eq=np.array(industryList[:29]+[e])
b_eq=np.array(mvIndustryIndex[:29]+[1])
bonds=[np.array([0,None])]*len(columns[2:])
for i in range(0,len(bonds)):
    bonds[i][0]=wDown[i]
    bonds[i][1]=wUp[i]
    bonds[i]=tuple(bonds[i])
res = optimize.linprog(c,A_ub,b_ub,A_eq,b_eq,bonds)

# ####test
# from scipy import optimize
# import numpy as np
#
# #确定c,A,b,Aeq,beq
# c = np.array([2,3,-5])
# A = np.array([[-2,5,-1],[1,3,1]])
# b = np.array([-10,12])
# Aeq = np.array([[1,1,1]])
# beq = np.array([7])
#
# #求解
# res = optimize.linprog(-c,A,b,Aeq,beq)
# print(res)