import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.seasonal import seasonal_decompose
import datetime as dt


class SarimaModel:
    """
    SARIMA Model予測用クラス
    参考: https://www.statsmodels.org/dev/generated/statsmodels.tsa.statespace.sarimax.SARIMAX.html
         
    
    Attributes
    ----------
    train: pd.DataFrame
        学習データ
    target: str
        予測対象名
    df_calender: pd.DataFrame
        東京都中央卸売市場　休業日
    exog: [None, str]
        外生変数名
    order: (int, int, int)
        非季節性パラメータ。(p,d,q) p: ARパラメータ、p時点過去まで使う, d:階差, q:MAパラメータ, q時点過去までのノイズを使う
    seasonal_order: (int, int, int, int)
        季節性パラメータ, The (P,D,Q,s) P: ARパラメータ、P時点過去まで使う, D:階差, Q:MAパラメータ, Q時点過去までのノイズを使う、s:周期性
    forecast_range: int
        何時点先まで予測するか。デフォルト30日先
    """
    
    def __init__(self, train, df_calender, target="quantity", exog=None, order=(1,1,1), seasonal_order=(1, 1, 1, 7), forecast_range=30):
        
        self.train = train
        self.target = target
        self.df_calender = df_calender
        self.exog = exog
        self.order = order
        self.seasonal_order = seasonal_order  
        self.forecast_range = forecast_range
    
    def fit(self):
        """学習"""
        sarima_model = sm.tsa.SARIMAX(self.train[self.target], exog=self.train[self.exog] if self.exog!=None else self.exog,
                                      order=self.order, seasonal_order=self.seasonal_order)
        sarima_fit_model = sarima_model.fit()
        # display(sarima_fit_model.summary())
        return sarima_fit_model
    
    def predict(self, sarima_fit_model):
        """予測"""
        #外生変数は学習データの中で最新の値を使用
        if self.exog != None:
            latest_exog_value = self.train.tail(1)[self.exog].values[0]
            # print(latest_exog_value)
            pred = sarima_fit_model.forecast(self.forecast_range, exog=[latest_exog_value]*self.forecast_range)
        else:
            pred = sarima_fit_model.forecast(self.forecast_range)
        
        #日曜日の値を0に補正
        min_date = pred.index.min()
        max_date = pred.index.max()
        holiday = self.df_calender.query("@min_date<=date<=@max_date and is_closed==1 and week_day==6")["date"]
        pred = pd.DataFrame(pred)
        pred.loc[holiday, "predicted_mean"] = 0
        
        return pred