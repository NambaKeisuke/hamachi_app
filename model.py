import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.seasonal import seasonal_decompose

class SarimaModel:
    """
    SARIMA Model予測用クラス
    参考: https://www.statsmodels.org/dev/generated/statsmodels.tsa.statespace.sarimax.SARIMAX.html
         
    
    Attributes
    ----------
    order : (int, int, int)
        非季節性パラメータ。(p,d,q) p: ARパラメータ、p時点過去まで使う, d:階差, q:MAパラメータ, q時点過去までのノイズを使う
    seasonal_order : (int, int, int, int)
        季節性パラメータ, The (P,D,Q,s) P: ARパラメータ、P時点過去まで使う, D:階差, Q:MAパラメータ, Q時点過去までのノイズを使う、s:周期性
    forecast_range : int
        何時点先まで予測するか。デフォルト30日先
    """
    
    def __init__(self, order=(1,1,1), seasonal_order=(1, 1, 1, 7), forecast_range=30):

        self.order = order
        self.seasonal_order = seasonal_order  
        self.forecast_range = forecast_range
    
    def fit(self, train):
        """学習"""
        sarima_model = sm.tsa.SARIMAX(train, order=self.order, seasonal_order=self.seasonal_order)
        sarima_fit_model = sarima_model.fit()
        display(sarima_fit_model.summary())
        return sarima_fit_model
    
    def predict(self, sarima_fit_model):
        """予測"""
        pred = sarima_fit_model.forecast(self.forecast_range)
        return pred