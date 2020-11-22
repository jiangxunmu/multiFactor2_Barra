import pandas as pd
import numpy as np
import copy
import matplotlib.pyplot as plt
pd.set_option('expand_frame_repr', False)
freeMV=pd.read_csv('C:/Users/Lenovo/Desktop/qta_program/freeMV_1.csv',parse_dates=['date'], index_col=['date'])

class Demo():
    def Layered(df,n,method):
        adj_price_pct = pd.read_csv('C:/Users/Lenovo/Desktop/qta_program/adj_price_pct.csv', parse_dates=['date'],index_col=['date'])
        MV = pd.read_csv('C:/Users/Lenovo/Desktop/qta_program/freeMV_1.csv', parse_dates=['date'],index_col=['date'])
        day_signal=copy.deepcopy(adj_price_pct)
        Size_signal=copy.deepcopy(df)
        equity=pd.DataFrame()
        for i in range(1,n+1):
            print(i)
            month_signal=pd.DataFrame()
            Size_signal[str(i)]=df.quantile((1/n)*i,axis=1)
            for stock in Size_signal.columns[:3843]:
                if i==1:
                    month_signal[stock] = (Size_signal[stock] < Size_signal[str(i)]) * Size_signal[stock] / Size_signal[stock]
                else:
                    month_signal[stock] = i*(Size_signal[stock] < Size_signal[str(i)])*(Size_signal[stock] > Size_signal[str(i-1)]) * Size_signal[stock] / Size_signal[stock]
            if method=='EW':
                month_signal=month_signal.iloc[:-6]
                month_signal=month_signal.resample('d').ffill()
                list=day_signal.index
                for date in list:
                    day_signal.loc[date]=month_signal.loc[date]
                    grouped = adj_price_pct.loc[date].groupby(day_signal.loc[date])
                    equity.loc[date,str(i)]=grouped.mean()[i]
                    equity['cum'+str(i)]=(equity[str(i)]+1).cumprod()
                plt.plot(equity['cum'+str(i)],label='group_'+str(i))
            if method=='MAV':
                Size = MV.apply(np.exp)
                weight = Size * month_signal
                weight = weight.replace(np.nan, 0)
                weight['sum'] = weight.sum(axis=1)
                for stock in weight.columns:
                    weight[stock] = weight[stock] / weight['sum']
                del weight['sum']
                weight = weight.iloc[:-6]
                weight = weight.resample('d').ffill()
                day_signal = copy.deepcopy(adj_price_pct)
                for date in adj_price_pct.index:
                    day_signal.loc[date] = weight.loc[date]
                equity = day_signal * adj_price_pct
                equity = equity.replace(np.nan, 0)
                equity[str(i)] = equity.sum(axis=1)
                equity['cum' + str(i)] = (equity[str(i)] + 1).cumprod()
                plt.plot(equity['cum' + str(i)], label='group_' + str(i))
        plt.legend()
        plt.show()


Demo.Layered(freeMV,5,'MAV')
Demo.Layered(freeMV,5,'EW')
