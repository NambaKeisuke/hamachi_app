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
    sarima = SarimaModel(forecast_range=int(forecast_range))
    sarima_fit = sarima.fit(train)
    test_pred = sarima.predict(sarima_fit)
    test_pred = pd.DataFrame(test_pred)
    test_pred["predicted_mean"].max()

    temp_df = df_hamachi.copy()
    temp_df = temp_df[f"{year}"]

    global test_pred_max
    test_pred_max = test_pred.loc[lambda df: df["predicted_mean"]==df["predicted_mean"].max()]

    fig = go.Figure(data=[
    go.Scatter(x=temp_df['date'], y=temp_df['quantity'], name='実績'),
    go.Scatter(x=test_pred.index, y=test_pred['predicted_mean'], name='予測'),
    go.Scatter(x=test_pred_max.index, y=test_pred_max['predicted_mean'], name='大量予想日', marker={'size': 10, 'symbol': 'star', 'color':'gold'}, ),
    ])
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
        - 本アプリケーションは以下のデータを用いて豊洲市場におけるハマチの卸売数量を予測しています
            - 東京卸売市場日報 (https://www.shijou-nippo.metro.tokyo.lg.jp/SN/SN_Sui_Nengetu.html)
            - 小売物価統計調査 (https://www.stat.go.jp/data/kouri/doukou/3.html)
            - 各種データ・資料 - 気象庁 (https://www.jma.go.jp/jma/menu/menureport.html)
            - 市場開場日・休業日年間カレンダー - 東京都中央卸売市場 (https://www.shijou.metro.tokyo.lg.jp/calendar/)
        """
    )

    input_button.click(graph, inputs=input, outputs=output_graph)
iface.launch()
