import pandas as pd


# 小売物価統計調査から、東京23区におけるブリの月次価格を引っ張ってくるコード
def get_household_survey():
    # e-Statにユーザー登録し、APIキーを取得しておくこと
    # URL: https://www.e-stat.go.jp/api/
    API_KEY = ""

    # 取得年月の設定
    latest_year = 2023
    year_period = 8
    years = list(range(latest_year, latest_year - year_period, -1))
    months = range(1, 13)
    periods = []
    for y in years:
        y = y * 1_000_000
        for m in months:
            ym = y + m * 100 + m
            periods.append(str(ym))
    periods = ("%2C").join(periods)

    # データ取得
    #url = f"http://api.e-stat.go.jp/rest/3.0/app/getSimpleStatsData?cdTab=01&cdCat02=03&cdArea=00000&cdTime={periods}&appId={API_KEY}&lang=J&statsDataId=0003343671&metaGetFlg=Y&cntGetFlg=N&explanationGetFlg=Y&annotationGetFlg=Y&sectionHeaderFlg=1&replaceSpChars=0"
    url = f"http://api.e-stat.go.jp/rest/3.0/app/getSimpleStatsData?cdTab=10&cdCat02=01111&cdArea=13100&cdTime={periods}&appId={API_KEY}&lang=J&statsDataId=0003421913&metaGetFlg=Y&cntGetFlg=N&explanationGetFlg=Y&annotationGetFlg=Y&sectionHeaderFlg=1&replaceSpChars=0"
    df = pd.read_csv(url, header=27)
    #df = pd.read_csv(url)
    return df


if __name__ == "__main__":
    df = get_household_survey()
    df.to_csv(r"./data/FEH_buri.csv", index=False)
