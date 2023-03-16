import datetime as dt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import gradio as gr
from model import SarimaModel

df_hamachi = pd.read_csv(r'./data/hamachi_price.csv', encoding='utf_8_sig')
df_hamachi["date"] = df_hamachi["date"].apply(lambda x: pd.to_datetime(str(x)))

df_hamachi = df_hamachi.set_index(df_hamachi["date"])
train = df_hamachi["quantity"]


def graph(forecast_range):
    today = dt.date.today()
    year = today.year
    # past_year = dt.date(today.year-int(number), today.month, today.day)
    sarima = SarimaModel(forecast_range=int(forecast_range))
    sarima_fit = sarima.fit(train)
    test_pred = sarima.predict(sarima_fit)
    test_pred = pd.DataFrame(test_pred)
    test_pred["predicted_mean"].max()

    temp_df = df_hamachi.copy()
    temp_df = temp_df[f"{year}"]

    test_pred_max = test_pred.loc[lambda df: df["predicted_mean"]==df["predicted_mean"].max()]

    fig = go.Figure(data=[
    go.Scatter(x=temp_df['date'], y=temp_df['quantity'], name='実績'),
    go.Scatter(x=test_pred.index, y=test_pred['predicted_mean'], name='予測'),
    go.Scatter(x=test_pred_max.index, y=test_pred_max['predicted_mean'], name='大量予想日', marker={'size': 10, 'symbol': 'star', 'color':'gold'}, ),
    ])
    return fig

# input = gr.Slider(1, 8, 1, step=1, label='last n years', info='今日から過去n年間におけるハマチの卸売数量の最大値をグラフで表示するだけ')

iface = gr.Interface(fn=graph, inputs=gr.Number(label="何日先まで予測しますか？"), outputs=gr.Plot())
iface.launch()
