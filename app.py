import datetime as dt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import gradio as gr
import get_fish_price
from model import SarimaModel

df_hamachi = pd.read_csv(r'./data/hamachi_price.csv', encoding='utf_8_sig')
df_hamachi["date"] = df_hamachi["date"].apply(lambda x: pd.to_datetime(str(x)))

today = dt.date.today()
year = today.year
month = today.month

# ハマチの卸売数量のデータを更新
if df_hamachi['date'].max().date() < today:
    start_date = df_hamachi['date'].max().date() + dt.timedelta(days=1)
    temp_df = get_fish_price.get_fish_price_data(start_date=start_date, end_date=today)
    df_hamachi = pd.concat([df_hamachi, temp_df])
    df_hamachi["date"] = df_hamachi["date"].apply(lambda x: pd.to_datetime(str(x)))
    df_hamachi.to_csv(r'./data/hamachi_price.csv', encoding='utf_8_sig', index=False)

df_hamachi["month"] = df_hamachi["date"].dt.month
df_hamachi["year"] = df_hamachi["date"].dt.year
#小売物価統計の最新の行を取得
df_hamachi_latest = df_hamachi.tail(1)

#小売物価統計調査データ
df_FEH = pd.read_csv("./data/FEH_buri.csv")
df_FEH["時間軸（月）"] = pd.to_datetime(df_FEH["時間軸（月）"], format='%Y年%m月')
df_FEH["year"] = df_FEH["時間軸（月）"].dt.year
df_FEH["month"] = df_FEH["時間軸（月）"].dt.month
df_FEH = df_FEH.sort_values(by=["year", "month"], ascending=False)
#小売物価統計の最新の行を取得
df_FEH_latest = df_FEH.head(1)
#ハマチの卸売数量のデータの最新月は、何カ月差か計算
delta = abs(df_hamachi_latest["year"].iloc[0] - df_FEH_latest["year"].iloc[0])*12\
        + abs(df_hamachi_latest["month"].iloc[0] - df_FEH_latest["month"].iloc[0])

#東京都中央卸売市場　休業日データ
df_calender = pd.read_csv("./data/toyosu_calender_2023.csv")
df_calender["date"] = pd.to_datetime(df_calender["date"])
df_calender["week_day"] = df_calender["date"].apply(lambda x: x.weekday())

#ハマチの卸売数量のデータと小売物価統計調査データをマージ
df_hamachi = pd.merge(left=df_hamachi, right=df_FEH[["year", "month", "value"]], on=["year", "month"],
        how="left")
#直近のデータの内、小売物価統計調査データがnanの箇所を最新の値で埋める
for i in range(delta-1, -1, -1):
    if month-i>0:
        df_hamachi.loc[(df_hamachi["year"]==year) & (df_hamachi["month"]==month-i),
           "value"
          ] = df_FEH_latest["value"].at[0]
    elif (month-i>-12)and (month-i<=0):
        df_hamachi.loc[(df_hamachi["year"]==year-1 & (df_hamachi["month"]==month-i+12)),
           "value"
          ] = df_FEH_latest["value"].at[0] 
    else:
        raise ValueError("小売物価統計調査データを更新してください")

df_hamachi = df_hamachi.set_index(df_hamachi["date"])
train = df_hamachi[["quantity", "value"]]
train.dropna(subset = ["value"], inplace=True)
def graph(forecast_range):
    sarima = SarimaModel(train=train, df_calender=df_calender, exog="value", forecast_range=int(forecast_range))
    sarima_fit = sarima.fit()
    test_pred = sarima.predict(sarima_fit)
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

def graph(forecast_range):
    # SARIMAモデルで予測
    sarima = SarimaModel(train=train, df_calender=df_calender, exog="value", forecast_range=int(forecast_range))
    sarima_fit = sarima.fit()
    test_pred = sarima.predict(sarima_fit)
    test_pred["predicted_mean"].max()

    temp_df = df_hamachi.copy()
    temp_df = temp_df[f"{year}"]

    global test_pred_max
    test_pred_max = test_pred.loc[lambda df: df["predicted_mean"]==df["predicted_mean"].max()]

    # グラフにプロット
    fig = go.Figure(data=[
    go.Scatter(x=temp_df['date'], y=temp_df['quantity'], name='実績'),
    go.Scatter(x=test_pred.index, y=test_pred['predicted_mean'], name='予測'),
    go.Scatter(x=test_pred_max.index, y=test_pred_max['predicted_mean'], name='大量予想日', marker={'size': 10, 'symbol': 'star', 'color':'gold'}, ),
    ])

    fig.update_layout(title=dict(text='ハマチの卸売数量予測結果',
                             x=0.5,
                             y=0.9,
                             xanchor='center'
                            ),
                    xaxis=dict(title='年月日'),
                    yaxis=dict(title='ハマチの卸売数量(kg)'))
    return fig

def text():
    return test_pred_max['predicted_mean']

with gr.Blocks() as iface:
    gr.Markdown(
        """
        # ハマチが大漁になる日を予測するアプリ
        - 本アプリでは、現在から入力された予測日までの、豊洲市場におけるハマチの卸売数量の予測推移グラフを表示します
        - 併せて、予測された推移内で卸売数量が最大となる日をグラフ上で示します
        """
    )
    with gr.Row():
        with gr.Column():
            input = gr.Number(label="何日先まで予測しますか？")
            input_button = gr.Button("予測する")
        with gr.Column():
            output_graph = gr.Plot()
    gr.Markdown(
        """
        ## 本アプリケーションについて
        - 本アプリケーションは現在から選択された日数までの期間における、豊洲市場におけるハマチの卸売数量の推移をS-ARIMAモデルを用いて予測し、卸売数量が最も多くなると予想される日を表示するアプリケーションです
        - 本アプリケーションではユーザーがアクセスしたタイミングでデータを自動更新しております
        - 本アプリケーションは以下のデータを用いて豊洲市場におけるハマチの卸売数量を予測しています
            - 東京卸売市場日報 (https://www.shijou-nippo.metro.tokyo.lg.jp/SN/SN_Sui_Nengetu.html)
            - 小売物価統計調査 (https://www.stat.go.jp/data/kouri/doukou/3.html)
            - 市場開場日・休業日年間カレンダー - 東京都中央卸売市場 (https://www.shijou.metro.tokyo.lg.jp/calendar/)
        """
    )

    input_button.click(graph, inputs=input, outputs=output_graph)
iface.launch()
