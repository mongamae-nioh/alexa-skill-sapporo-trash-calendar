# SapporoTrashCalendar
- 札幌市のごみ収集日に関するAlexaスキル
  - python3系へ移行しましたので（[こちら](https://github.com/mongamae-nioh/alexa-skill-sapporo-trash-calendar-python3)）をお使いください
- スキルは[こちら](https://www.amazon.co.jp/mongamae-nioh-%E6%9C%AD%E5%B9%8C%E3%81%94%E3%81%BF%E3%81%AA%E3%81%92%E3%82%AB%E3%83%AC%E3%83%B3%E3%83%80%E3%83%BC/dp/B07GP7XFBW/ref=sr_1_1?s=digital-skills&ie=UTF8&qid=1537202805&sr=1-1&keywords=%E6%9C%AD%E5%B9%8C)
- [Alexa Skills Kit SDK for Python ](https://github.com/alexa-labs/alexa-skills-kit-sdk-for-python)を使って開発

## 構成インテント
### LaunchRequest

起動時に呼び出される。収集エリア未設定（=初回起動時）の場合は収集エリアを設定する。

### SelectWardIntent

収集エリア設定時に呼び出される。お住まいの区を設定する。

### SelectCalendarIntent
収集エリア設定時に呼び出される。カレンダー番号を設定する。

### AMAZON.YesIntent
収集エリア設定時に呼び出される。「はい」でエリア確定。

### AMAZON.NoIntent
収集エリア設定時に「いいえ」と答えると設定が初期化される。

### WhatTrashDayIntent
日付や曜日を発話した際に呼び出される。その日に収集されるごみを返答する。

### NextWhenTrashDayIntent
ごみの種類を発話した際に呼び出される。そのごみの次の収集日と曜日を返答する。

### AMAZON.HelpIntent
スキルの使い方を返答する。

## データベース
- DynamoDBを使用
- ハッシュキーを区とエリア番号、ソートキーを日付にしてこの二つのキーでアイテムが一意になるようにした。

### 構成
| WardCalNo | Date | TrashNo |
----|----|----|
| 区とエリア番号 | 日付 | ごみ種別番号 |

### DynamoDB作成コマンド
- DynamoDBLocalを使って検証するときはAWS CLIで作成する
- dynamodb-table-schema.jsonへテーブル定義を記載している
- 以下コマンドでテーブルを作成する

```
aws dynamodb create-table --cli-input-json file://dynamodb-table-schema.json --endpoint-url http://localhost:8000
```

jsonなしで作成する場合は以下コマンドで作成

```
aws dynamodb create-table \
--table-name SapporoTrashCalendar \
--attribute-definitions \
    AttributeName=Date,AttributeType=S \
    AttributeName=WardCalNo,AttributeType=S \
--key-schema AttributeName=WardCalNo,KeyType=HASH AttributeName=Date,KeyType=RANGE \
--provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5
```


## ファイル構成
- SapporoTrash.py
  - スキル本体のコード
  - Alexa Skills Kit SDK for Pythonを利用
- convert_from_csv_to_json.py
  - DynamoDBへINSERTするために札幌市が公開しているごみ収集カレンダーのオープンデータをjsonへ変換するスクリプト
  - スキルで使っているごみ種別番号とオープンデータの番号がバラバラだったので作成
- delete_item_perday.py
  - 過去のごみデータは意味が無いのとDynamoDBのサイズを軽くしたいので前日の収集データを削除するスクリプト
  - Lambdaで毎日0:00に実行
- insert_dynamodb_local.py
  - DynamoDB LocalへデータをINSERTするスクリプト
  - DB名やリージョンは適宜変更してください
  - DynamoDBをローカルで検証したい場合はDynamoDB Localがオススメ
  - [クラメソさんの記事](https://dev.classmethod.jp/etc/try_dynamodb_local/)に詳しく載っている
- insert_dynamodb_production.py
  - 本番のDynamoDBへデータをINSERTするスクリプト
  - リージョンは適宜変更してください
  - 認証はaws configureで設定
  - IAMは特定のテーブルのみ操作できるように設定したほうがよいです
    - 参考：[AWSドキュメント](https://docs.aws.amazon.com/ja_jp/IAM/latest/UserGuide/reference_policies_examples_dynamodb_specific-table.html)
  - memo: INSERTするときはDynamoDBのテーブル編集権限を持つAWS権限へ切り替える
    - export AWS_DEFAULT_PROFILE=ask_cli_default -> aws configure listで確認
  


## ごみ収集データについて
- 2018/9/30分までは収集カレンダーのPDFからデータ起こし
- 2018/10/1~は札幌市から公開されている[オープンデータ](https://ckan.pf-sapporo.jp/dataset/garbage_collection_calendar)を利用
- オープンデータを整形してboto3でDynamoDBへインサートする
- [2020年8月公開データ](https://ckan.pf-sapporo.jp/dataset/garbage_collection_calendar/resource/3e7862c1-c9df-4b21-b6cf-aca9b89e60c6)ではヘッダが**中央区①**のように変わったためcsvの①〜⑦を置換するロジックをJSON作成pythonへ追加
- [2021年9月公開データ](https://ckan.pf-sapporo.jp/dataset/281fc9c2-7ca5-4aed-a728-0b588e509686/resource/b9a4cf2b-8ffd-4be2-8431-f2d6ef129051)では**曜日**のカラム名が**曜**へ変更された
- [2021年10月公開データ](https://ckan.pf-sapporo.jp/dataset/garbage_collection_calendar/resource/28f303ea-97c2-4c89-8539-b17a5661b0da)のデータ構造は前年から変更なし
