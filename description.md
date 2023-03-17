# はまちが今年一番大漁になる日を予測するアプリ
- READMEをいじるとhugging face上でアプリが動かなくなるのでとりあえずこちらに

## データ
- hamachi_price.csv
    - 東京卸売市場日報(https://www.shijou-nippo.metro.tokyo.lg.jp/SN/SN_Sui_Nengetu.html)より取得
    - 豊洲市場（築地市場）におけるハマチの高値、中値、安値、卸売数量のデータ
    - 2018年10月11日からは豊洲市場のデータ、それまでは築地市場のデータ
    - 価格が欠損、卸売数量が0の行はだいたい休業日

- household_survey.csv
    - 家計調査の月別支出より取得

- toyosu_calender_2023.csv
    - 東京都中央卸売市場(https://www.shijou.metro.tokyo.lg.jp/calendar/)をもとに作成
    - 2023年における豊洲市場の休業日のデータ。is_closedが1なら休業日

- FEH_buri.csv
    - 小売物価統計調査(https://www.stat.go.jp/data/kouri/doukou/3.html)より取得
    - 日本の主要都市における年次のブリの平均価格
    - 期間は2000年-2021年

- nagasaki_weather
    - 気象庁(https://www.jma.go.jp/jma/menu/menureport.html)より取得。長崎県島原の天気情報
    - 長崎県島原のあたりにブリの養殖場があるらしいので取得してみた