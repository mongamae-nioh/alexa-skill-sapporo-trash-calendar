# SapporoTrashCalendar
- 札幌市のごみ収集日に関するAlexaスキル
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

## ファイル構成
- SapporoTrash.py
  - スキル本体のコード
  - Alexa Skills Kit SDK for Pythonを利用
