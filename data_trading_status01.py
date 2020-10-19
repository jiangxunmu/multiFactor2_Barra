import pandas as pd

#from datetime import datetime
#ST = pd.read_csv('E:\PHBS\QTA\data\ST.csv')
###增加一列date格式的日期
#ST['datetime']=ST['date']
#for i in range(len(ST)):
 #   ST.loc[i, 'datetime'] = datetime.strptime(ST.loc[i, 'datetime'], '%Y/%m/%d')
  #  ST.loc[i, 'datetime'] = datetime.date(ST.loc[i, 'datetime'])
#ST.isnull().sum().sum()

trading_status = pd.read_csv('E:\PHBS\QTA\data\\trading_status.csv', encoding='GBK')##读取中文的时候要设定编码为‘GBK’
trading_status.fillna(0, inplace=True)##填充空值
trading_status.replace(['交易', '停牌', 'XD', 'XR', 'DR', 'N'], [1, 0, 1, 1, 1, 2], inplace=True)
stocks = trading_status.columns
stocks = stocks[1:len(stocks)]
daynum = len(trading_status.index)
##IPO180天的数据不能使用
for a in stocks:
    n = trading_status[trading_status[a] == 2].index.tolist()
    if n != []:
        for i in range(n[0], min(n[0]+180, daynum)):
            trading_status.loc[i, a] = 0
trading_status.to_csv('E:\PHBS\QTA\data\\trading_status01.csv', index=False)

