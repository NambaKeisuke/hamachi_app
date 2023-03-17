import codecs
import io
import random
import requests
import time
from datetime import date, timedelta
from tqdm import tqdm
from typing import Generator, Tuple

import numpy as np
import pandas as pd


def date_range(
    start: date, stop: date, step: timedelta = timedelta(1)
) -> Generator[date, None, None]:
    """startからendまで日付をstep日ずつループさせるジェネレータ"""
    current = start
    while current < stop:
        yield current
        current += step


def get_url(download_date: date) -> Tuple[str, str]:
    """ダウンロードするURLと日付の文字列を返す"""
    month = download_date.strftime("%Y%m")
    day = download_date.strftime("%Y%m%d")
    return (
        f"https://www.shijou-nippo.metro.tokyo.lg.jp/SN/{month}/{day}/Sui/Sui_K1.csv",
        day,
    )


def content_wrap(content):
    """1行目にヘッダ行が来るまでスキップする"""
    buffer = ""
    first = True
    for line in io.BytesIO(content):
        line_str = codecs.decode(line, "shift-jis")
        if first:
            if "品名" in line_str:
                first = False
                buffer = line_str
            else:
                continue
        else:
            buffer += line_str
    return io.StringIO(buffer)


def insert_data(data, day, low_price, center_price, high_price, quantity):
    """ "データをリストに追加する"""
    data["date"].append(day)
    data["low_price"].append(low_price)
    data["center_price"].append(center_price)
    data["high_price"].append(high_price)
    data["quantity"].append(quantity)


def to_numeric(x):
    """文字列を数値に変換する"""
    if isinstance(x, str):
        return float(x)
    else:
        return x


def get_fish_price_data(start_date: date, end_date: date) -> pd.core.frame.DataFrame:
    """
    東京卸売市場からデータを引っ張ってくる

    :param start_date: 開始日
    :param end_date: 終了日
    :return: はまちの値段を結合したデータ
    """
    data = {
        "date": [],
        "low_price": [],
        "center_price": [],
        "high_price": [],
        "quantity": [],
    }
    iterator = tqdm(
        date_range(start_date, end_date), total=(end_date - start_date).days
    )

    for download_date in iterator:
        url, day = get_url(download_date)
        iterator.set_description(day)
        response = requests.get(url)

        # URLが存在しないとき
        if response.status_code == 404:
            insert_data(data, day, np.nan, np.nan, np.nan, 0)
            continue
        assert (
            response.status_code == 200
        ), f"Unexpected HTTP response. Please check the website {url}."

        df = pd.read_csv(content_wrap(response.content))

        # 欠損値補完
        price_cols = ["安値(円)", "中値(円)", "高値(円)"]
        for c in price_cols:
            df[c].mask(df[c] == "-", np.nan, inplace=True)
            df[c].mask(df[c] == "−", np.nan, inplace=True)
        df["卸売数量"].mask(df["卸売数量"] == "-", np.nan, inplace=True)
        df["卸売数量"].mask(df["卸売数量"] == "−", np.nan, inplace=True)


        # 品目 == はまち の行だけ抽出
        df_aji = df.loc[df["品名"] == "はまち", ["卸売数量"] + price_cols]

        # あじの販売がなかったら欠損扱いに
        if len(df_aji) == 0:
            insert_data(data, day, np.nan, np.nan, np.nan, 0)
            continue

        isnan = lambda x: isinstance(x, float) and np.isnan(x)
        # はまちの販売実績を調べる
        low_prices = []
        center_prices = []
        high_prices = []
        quantities = []
        for i, row in enumerate(df_aji.iloc):
            lp, cp, hp, q = row[price_cols + ["卸売数量"]]
            lp, cp, hp, q = (
                to_numeric(lp),
                to_numeric(cp),
                to_numeric(hp),
                to_numeric(q),
            )

            # 中値だけが記録されている -> 価格帯が1個だけなので高値、安値も中値と同じにしておく
            if isnan(lp) and isnan(hp) and (not isnan(cp)):
                low_prices.append(cp)
                center_prices.append(cp)
                high_prices.append(cp)

            # 高値・安値があり中値がない -> 価格帯2個、とりあえず両者の平均を中値とする
            elif (not isnan(lp)) and (not isnan(hp)) and isnan(cp):
                low_prices.append(lp)
                center_prices.append((lp + hp) / 2)
                high_prices.append(hp)
            else:
                low_prices.append(lp)
                center_prices.append(cp)
                high_prices.append(hp)

            if isnan(row["卸売数量"]):
                quantities.append(0)
            else:
                quantities.append(q)

        low_price = int(min(low_prices))
        center_price = int(sum(center_prices) / len(center_prices))
        high_price = int(max(high_prices))
        quantity = int(float(sum(quantities)))

        # 保存
        insert_data(data, day, low_price, center_price, high_price, quantity)
        # 短期間にアクセスが集中しないようにクールタイムを設定
        time.sleep(max(0.5 + random.normalvariate(0, 0.3), 0.1))
    # DataFrameを作成
    df = pd.DataFrame(data)
    return df


if __name__ == "__main__":
    start_date = date(2020, 12, 21)
    end_date = date(2020, 12, 26)
    df = get_fish_price_data(start_date=start_date, end_date=end_date)
    df.to_csv("fish_price.csv", index=False)
