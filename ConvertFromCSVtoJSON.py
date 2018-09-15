# -*- coding: utf-8 -*-

import pandas as pd
import json
import collections as cl
import re

# ファイル
#inputfile = 'C:/Users/admin/PycharmProjects/SapporoTrashCalendar/2017100120191008garvagecollectioncalendar.old.csv'
inputfile = '2017100120191008garvagecollectioncalendar.csv'
tempfile = 'temp.csv'
outputfile = 'insert-dynamodb.json'

# オープンデータ読み込み
with open(inputfile, 'r', encoding='utf-8') as f:
    filedata = f.read()

# DynamoDBへINSERTするために置換
dic = {
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
    '厚別区': 'atsubetsu-'
}

for key, value in dic.items():
    filedata = filedata.replace(key, value)

# 中間ファイル生成
with open(tempfile, 'w', encoding='utf-8') as f:
    f.write(filedata)

# DynamoDBにINSERTしない"曜日"をカットするためのリスト作成
list = list(range(2, 48))
list.append(0)

# "曜日"以外を中間ファイルへ出力
df = pd.read_csv(tempfile, encoding="utf-8", sep=',',usecols=list)

# 札幌市のオープンデータのごみ番号をゴミスキル用に置換
## びん・缶・ペット 8 -> 4
## 容器プラ 9 -> 3
## 雑がみ 10 -> 5
## 枝・葉・草 11 -> 6
df = df.replace({8: 4, 9: 3, 10: 5, 11: 6}, regex=True)
# 収集無し NaN -> 0
df = df.fillna(0)

# 中間ファイル
df.to_csv(tempfile, index=False)

# 全エリアのDynamoDB INSERT用ファイル生成
# 書き込まれる順番固定
od = cl.OrderedDict()
with open(outputfile, 'a') as f:
    for i in range(1, 47):
        df = pd.read_csv(tempfile, encoding="utf-8", sep=',',usecols=[0, i])
        columnsname = df.columns.values
        wardcalno = columnsname[1]
        for index, row in df.iterrows():
            # 小数点削除
            trashno = round(row[wardcalno])
            # 各キーの値
            od['WardCalNo'] = wardcalno
            od['Date'] = row['?Date']
            od['TrashNo'] = trashno
            # ファイル生成
            json.dump(od,f,indent=4, separators=(',', ': '))

# DynamoDBへINSERTするためにjsonを整形
dic2 = {
    '}': '},\n',
}

with open(outputfile, 'r', encoding='utf-8') as f:
    filedata = f.read()
    for key, value in dic2.items():
        filedata = filedata.replace(key, value)
        # ファイルの先頭を [ へ置換
        result = re.sub('\A', '[\n', filedata)
    # 最後のカンマ消して ] へ置換
    result = result[:-2]
    result = re.sub('\Z', '\n]', result)

with open(outputfile, 'w', encoding='utf-8') as f:
    f.write(result)
