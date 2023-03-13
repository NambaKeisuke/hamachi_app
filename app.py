import datetime as dt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import gradio as gr

df_hamachi = pd.read_csv(r'data/hamachi_price.csv', encoding='utf_8_sig')
df_hamachi['date'] = pd.to_datetime(df_hamachi['date'], format='%Y%m%d')
df_hamachi['date'] = df_hamachi['date'].apply(lambda x: x.date())




def graph(number):
    today = dt.date.today()
    past_year = dt.date(today.year-int(number), today.month, today.day)

    temp_df = df_hamachi.copy()
    temp_df = temp_df[temp_df['date'].between(past_year, today)]
    temp_df.reset_index(drop=True, inplace=True)

    temp_df_max = temp_df[temp_df['quantity'] == temp_df['quantity'].max()]
    temp_df_max = temp_df[temp_df['quantity'] == temp_df['quantity'].max()]

    fig = go.Figure(data=[
    go.Scatter(x=temp_df['date'], y=temp_df['quantity'], name='quantity'),
    go.Scatter(x=temp_df_max['date'], y=temp_df_max['quantity'], name='max'),
    ])
    return fig

input = gr.Slider(1, 8, 1, step=1, label='last n years', info='今日から選択された数字nまでの過去n年間における卸売数量の最大値をグラフで表示するだけ')

iface = gr.Interface(fn=graph, inputs=input, outputs=gr.Plot())
iface.launch()