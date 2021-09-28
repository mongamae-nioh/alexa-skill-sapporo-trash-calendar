# -*- coding: utf-8 -*-

import pandas as pd
import json
import collections as cl
import re

# Number of garbage collection patterns
number_of_collections = 46

# ファイル
inputfile = 'b9a4cf2b-8ffd-4be2-8431-f2d6ef129051'
tempfile = 'temp.csv'
outputfile = 'insert-dynamodb.json'

# オープンデータ読み込み
with open(inputfile, 'r', encoding='utf-8') as f:
    filedata = f.read()

# DynamoDBへINSERTするために置換
dict = {
    '日付': 'Date',
    '/': '-',
    '中央区': 'chuo-',
    '東区': 'higashi-',
    '西区': 'nishi-',
    '南区': 'minami-',
    '北区': 'kita-',
    '豊平区': 'toyohira-',
    '白石区': 'shiroishi-',
    '手稲区': 'teine-',
    '清田区': 'kiyota-',
    '厚別区': 'atsubetsu-',
    # convert month format for dynamodb
    '-1-': '-01-',
    '-2-': '-02-',
    '-3-': '-03-',
    '-4-': '-04-',
    '-5-': '-05-',
    '-6-': '-06-',
    '-7-': '-07-',
    '-8-': '-08-',
    '-9-': '-09-',
    # convert day format for dynamodb
    '-1,': '-01,',
    '-2,': '-02,',
    '-3,': '-03,',
    '-4,': '-04,',
    '-5,': '-05,',
    '-6,': '-06,',
    '-7,': '-07,',
    '-8,': '-08,',
    '-9,': '-09,'
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

# format change(str -> date)
df['Date'] = pd.to_datetime(df['Date'])

# 札幌市のオープンデータのごみ番号をゴミスキル用に置換
## びん・缶・ペット 8 -> 4
## 容器プラ 9 -> 3
## 雑がみ 10 -> 5
## 枝・葉・草 11 -> 6
#df = df.replace({8: 4, 9: 3, 10: 5, 11: 6}, regex=True)
df = df.replace(8, 4).replace(9, 3).replace(10, 5).replace(11, 6)
# 収集無し NaN -> 0
df = df.fillna(0)

# 中間ファイル
df.to_csv(tempfile, index=False)
print(df)

# 全エリアのDynamoDB INSERT用ファイル生成
# 書き込まれる順番固定
od = cl.OrderedDict()
with open(outputfile, 'a') as f:
    for i in range(1, number_of_collections+1):
        df = pd.read_csv(tempfile, encoding="utf-8", sep=',',usecols=[0, i])
#        print(df)
        columnsname = df.columns.values
        wardcalno = columnsname[1]
#        print(wardcalno)

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