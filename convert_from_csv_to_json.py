# -*- coding: utf-8 -*-

import pandas as pd
import json
import collections as cl
import re
import sys

# ゴミ収集パターンの数(エリアごとの収集データを作るループを回すときに使う)
number_of_collections = 46

# ファイル
inputfile = sys.argv[1]  # オープンデータファイル
tempfile = 'temp.csv'  # オープンデータを加工して使うための中間ファイル
outputfile = sys.argv[2]  # DynamoDBへINSERTするファイル

# オープンデータ読み込み
with open(inputfile, 'r', encoding='utf-8') as f:
    filedata = f.read()

# DynamoDBへINSERTするために置換
dict = {
    '日付': 'Date',
    '/': '-',
    # 実際のCSVヘッダーに基づく変換
    '中央区1': 'chuo-1',
    '中央区2': 'chuo-2',
    '中央区3': 'chuo-3',
    '中央区4': 'chuo-4',
    '中央区5': 'chuo-5',
    '中央区6': 'chuo-6',
    '豊平区1': 'toyohira-1',
    '豊平区2': 'toyohira-2',
    '豊平区3': 'toyohira-3',
    '豊平区4': 'toyohira-4',
    '清田区1': 'kiyota-1',
    '清田区2': 'kiyota-2',
    '北区1': 'kita-1',
    '北区2': 'kita-2',
    '北区3': 'kita-3',
    '北区4': 'kita-4',
    '北区5': 'kita-5',
    '北区6': 'kita-6',
    '東区1': 'higashi-1',
    '東区2': 'higashi-2',
    '東区3': 'higashi-3',
    '東区4': 'higashi-4',
    '東区5': 'higashi-5',
    '東区6': 'higashi-6',
    '白石区1': 'shiroishi-1',
    '白石区2': 'shiroishi-2',
    '白石区3': 'shiroishi-3',
    '白石区4': 'shiroishi-4',
    '厚別区1': 'atsubetsu-1',
    '厚別区2': 'atsubetsu-2',
    '厚別区3': 'atsubetsu-3',
    '厚別区4': 'atsubetsu-4',
    '南区1': 'minami-1',
    '南区2': 'minami-2',
    '南区3': 'minami-3',
    '南区4': 'minami-4',
    '南区5': 'minami-5',
    '南区6': 'minami-6',
    '南区7': 'minami-7',
    '西区1': 'nishi-1',
    '西区2': 'nishi-2',
    '西区3': 'nishi-3',
    '西区4': 'nishi-4',
    '手稲区1': 'teine-1',
    '手稲区2': 'teine-2',
    '手稲区3': 'teine-3',
    # convert month format for dynamodb
    # '-1-': '-01-',
    # '-2-': '-02-',
    # '-3-': '-03-',
    # '-4-': '-04-',
    # '-5-': '-05-',
    # '-6-': '-06-',
    # '-7-': '-07-',
    # '-8-': '-08-',
    # '-9-': '-09-',
    # # convert day format for dynamodb
    # '-1,': '-01,',
    # '-2,': '-02,',
    # '-3,': '-03,',
    # '-4,': '-04,',
    # '-5,': '-05,',
    # '-6,': '-06,',
    # '-7,': '-07,',
    # '-8,': '-08,',
    # '-9,': '-09,'
}

# convert month and day format for dynamodb
for key, value in dict.items():
    filedata = filedata.replace(key, value)

dict2 = {
    # 2020年8月のデータではヘッダが中央区①のような表示になったため置換対象を追加
    '①': '1',
    '②': '2',
    '③': '3',
    '④': '4',
    '⑤': '5',
    '⑥': '6',
    '⑦': '7'
}

# convert header format for dynamodb
for key, value in dict2.items():
    filedata = filedata.replace(key, value)

# 中間ファイル生成
with open(tempfile, 'w', encoding='utf-8') as f:
    f.write(filedata)

# スキルに不要な列以外を読み込む
# オープンデータのカラム名はなぜか「曜」になっている
exclude_columns = ["_id", "曜"]
df = pd.read_csv(tempfile, encoding="utf-8", sep=',', usecols=lambda x: x not in exclude_columns)

# DynamoDBへINSERTするためにフォーマット変換
df['Date'] = pd.to_datetime(df['Date'])

# 札幌市のオープンデータのごみ番号をゴミスキル用に置換
# スキル作成後にオープンデータが公開されたためごみ番号にズレあり
## びん・缶・ペット 8 -> 4
## 容器プラ 9 -> 3
## 雑がみ 10 -> 5
## 枝・葉・草 11 -> 6
df = df.replace(8, 4).replace(9, 3).replace(10, 5).replace(11, 6)
# 収集無し NaN -> 0
df = df.fillna(0)

# 中間ファイルをcsvへ変換
df.to_csv(tempfile, index=False)

# 全エリアのDynamoDB INSERT用ファイル生成
# 書き込み順番を固定するためodを使う
od = cl.OrderedDict()
with open(outputfile, 'a') as f:
    for i in range(1, number_of_collections+1):
        df = pd.read_csv(tempfile, encoding="utf-8", sep=',',usecols=[0, i])
        columnsname = df.columns.values
        wardcalno = columnsname[1]

        for index, row in df.iterrows():
            # 小数点削除
            trashno = round(row[wardcalno])
            # 各キーの値
            od['WardCalNo'] = wardcalno
            od['Date'] = row['Date']
            od['TrashNo'] = trashno
            # ファイル生成
            json.dump(od,f,indent=4, separators=(',', ': '))

# DynamoDBへINSERTするためにjsonを整形
dict3 = {
    '}': '},\n',
}

with open(outputfile, 'r', encoding='utf-8') as f:
    filedata = f.read()
    for key, value in dict3.items():
        filedata = filedata.replace(key, value)
        # ファイルの先頭を [ へ置換
        result = re.sub('\A', '[\n', filedata)
    # 最後のカンマ消して ] へ置換
    result = result[:-2]
    result = re.sub('\Z', '\n]', result)

with open(outputfile, 'w', encoding='utf-8') as f:
    f.write(result)