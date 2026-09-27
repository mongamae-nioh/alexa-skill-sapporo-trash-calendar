# ごみ収集データ 年次更新 手順書（Runbook）

年に1回、札幌市のオープンデータから翌年度（10/1〜翌9/30）のごみ収集カレンダーを取り込み、
DynamoDB（ローカル → 本番）へ投入する作業の手順。
**人間は手順を覚えていない前提**で、Claude がこの文書だけで同じ品質で再現できるように書いている。

最終実施: 2026-09-27（2026-10-01〜2027-09-30 分、16,790件）

---

## 0. 絶対に守ること（安全ルール）

| # | ルール | 理由 |
|---|---|---|
| 1 | **本番のテーブル・アイテムは削除しない。本番は「追加のみ」** | 本番テーブルは稼働中の Alexa スキルが参照している。過去データは Lambda が毎日削除するので手で消す必要はない（[ADR-0001](../adr/0001-production-add-only.md)） |
| 2 | **ローカル操作時は必ず `AWS_ENDPOINT_URL_DYNAMODB=http://localhost:8000` を付け、実行前に endpoint を assert する** | `batch_insert_to_dynamodb.py` / `delete_all_items.py` などはコード上 **本番がデフォルト**。付け忘れると本番に書き込む・消す（[ADR-0002](../adr/0002-local-endpoint-via-env.md)） |
| 3 | 本番投入前に **既存データと日付が重複しないこと** を確認する | `put_item` は同一キーを黙って上書きする |
| 4 | 本番投入は **人間の明示的な OK を得てから** 行う | 外部公開中サービスへの書き込みのため |

---

## 1. 前提・環境

- Python: `/opt/anaconda3/bin/python`（3.12, pandas / boto3 入り）で動作実績あり。`requirement.txt` 参照
- DynamoDB Local: `docker-compose.yaml`（`amazon/dynamodb-local`, port 8000, `-sharedDb`, データは `docker/dynamodb/`）
  - `-sharedDb` なので認証情報・リージョンはダミーで良い
- AWS 認証: `~/.aws/credentials` の default プロファイル、リージョン `ap-northeast-1`
  - DynamoDB 書き込み権限のある IAM ユーザーであることを `aws sts get-caller-identity` で確認
  - （README にある `ask_cli_default` プロファイル切り替えのメモは古い。2026年時点では default で投入できた）
- テーブル: `SapporoTrashCalendar`
  - HASH: `WardCalNo`（例 `chuo-1`）, RANGE: `Date`（`YYYY-MM-DD` 文字列）, 属性 `TrashNo`（数値）
  - 本番は PAY_PER_REQUEST（オンデマンド）なので書き込みスロットリングの心配はほぼない

---

## 2. 手順

### Step 1. オープンデータ取得
- 公開時期: 毎年 **9月頃**。投入期限は **10/1 より前**
- 取得元: [DATA-SMART CITY SAPPORO](https://data.pf-sapporo.jp/) / [CKAN: garbage_collection_calendar](https://ckan.pf-sapporo.jp/dataset/garbage_collection_calendar)
- 保存名: `garvagecollectioncalendarYYYY10.csv`（YYYY = 開始年。綴りは歴史的経緯で `garvage` のまま）

### Step 2. CSV の事前検証
データ構造は年によって変わったことがある（下の「過去の変更履歴」参照）。変換前に必ず確認する。

```sh
python -c "
import pandas as pd
df = pd.read_csv('garvagecollectioncalendarYYYY10.csv', encoding='utf-8-sig')
print(df.shape)                          # (365 or 366, 48) を期待
print(list(df.columns))                  # 日付, 曜, 中央区1..手稲区3 を期待
print(df.iloc[0,0], df.iloc[-1,0])       # YYYY-10-01, (YYYY+1)-09-30 を期待
print(sorted(map(str, pd.unique(df.iloc[:,2:].values.ravel()))))
# ['0.0','1.0','10.0','11.0','2.0','8.0','9.0','nan'] の部分集合を期待
"
```

チェック項目:
- [ ] 行数 = その年度の日数（**うるう年に注意**: 2027-10〜2028-09 は 2028-02-29 を含み **366行**）
- [ ] 列数 48（日付・曜 + 46エリア）。エリア数が変わっていたら `convert_from_csv_to_json.py` の `number_of_collections` と置換辞書、`delete_item_perday.py` の `wardtaple` の更新が必要
- [ ] 列名が `convert_from_csv_to_json.py` の置換辞書（`中央区1` → `chuo-1` 等）と一致する
- [ ] 日付が `YYYY-MM-DD`（`/` 区切りでもスクリプトが `-` に置換する）
- [ ] ごみ番号が既知の値のみ（未知の番号が出たら下の対応表とスキル本体 `SapporoTrash.py` の確認が必要）

### Step 3. JSON へ変換
```sh
python convert_from_csv_to_json.py garvagecollectioncalendarYYYY10.csv insert-dynamodb.json
```
- 警告・エラーが出ないこと
- 検証:
```sh
python -c "import json;d=json.load(open('insert-dynamodb.json'));print(len(d),d[0],d[-1])"
```
- 件数 = **46 × 日数**（365日 → 16,790 / 366日 → 16,836）
- 副産物 `temp.csv` も更新される（中間ファイル。git 管理されている）

### Step 4. ローカル（DynamoDB Local）で検証
```sh
docker compose up -d        # dynamodb-local コンテナが起動済みなら不要（docker ps で確認）
export AWS_ACCESS_KEY_ID=dummy AWS_SECRET_ACCESS_KEY=dummy \
       AWS_DEFAULT_REGION=ap-northeast-1 AWS_ENDPOINT_URL_DYNAMODB=http://localhost:8000
```

4-1. ローカルを空にする（テーブル削除 → 再作成。**ローカル限定**。endpoint を assert してから実行）
```sh
python -c "
import boto3
c = boto3.client('dynamodb')
assert c.meta.endpoint_url == 'http://localhost:8000', c.meta.endpoint_url
c.delete_table(TableName='SapporoTrashCalendar')
c.get_waiter('table_not_exists').wait(TableName='SapporoTrashCalendar')
" && python create_dynamodb_table.py
```
（テーブルが存在しない初回は delete をスキップして `create_dynamodb_table.py` のみ）

4-2. 投入
```sh
python -c "import boto3;assert boto3.resource('dynamodb').meta.client.meta.endpoint_url=='http://localhost:8000'" \
  && python batch_insert_to_dynamodb.py insert-dynamodb.json
```

4-3. 検証: Scan でページングしながら件数カウント（= Step 3 の件数）、代表アイテムを `get_item`。
その後 **人間にローカルでの動作確認を依頼**し、OK をもらう。

### Step 5. 本番へ追加投入
**別シェル or `unset AWS_ENDPOINT_URL_DYNAMODB AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY` で環境変数を必ず外す。**

5-1. 接続確認（読み取りのみ）
```sh
aws sts get-caller-identity
aws configure list      # region = ap-northeast-1
```

5-2. 既存データとの重複確認（本番は過去データが日次削除されるので数百件程度しかないのが正常）
```sh
python -c "
import boto3, json
t = boto3.resource('dynamodb', region_name='ap-northeast-1').Table('SapporoTrashCalendar')
assert 'amazonaws.com' in t.meta.client.meta.endpoint_url
items=[]; kw={'ProjectionExpression':'#d','ExpressionAttributeNames':{'#d':'Date'}}
while True:
    r=t.scan(**kw); items+=r['Items']
    if 'LastEvaluatedKey' not in r: break
    kw['ExclusiveStartKey']=r['LastEvaluatedKey']
ds=[i['Date'] for i in items]; new=[i['Date'] for i in json.load(open('insert-dynamodb.json'))]
print('prod', len(ds), min(ds), max(ds)); print('new', min(new), max(new)); print('overlap', max(ds) >= min(new))
"
```
- `overlap False` を確認。True なら **止めて人間に相談**（上書きになるため）
- 本番の既存件数を控えておく（5-4 で使う）

5-3. 人間の OK を得てから投入
```sh
python batch_insert_to_dynamodb.py insert-dynamodb.json
```

5-4. 検証
- Scan（`Select='COUNT'`・ページング）で総件数 = **既存件数 + 投入件数**
- `get_item` で 初日・最終日・既存データ1件 を確認（既存データが上書きされていないこと）
- `describe_table` の `ItemCount` は約6時間ごと更新の概算値なので検証に使わない

### Step 6. 記録・コミット
- README の「ごみ収集データについて」に当年データの URL と構造変更の有無を追記
- この Runbook の「最終実施」と「実施ログ」を更新
- `.claude/plans/project-status.md` を更新
- コミット（過去例: `insert 2025-2026 data`）: CSV / `insert-dynamodb.json` / `temp.csv` / スクリプト変更

---

## 3. ごみ番号の対応表

オープンデータ公開前にスキルを作ったため番号がずれている。変換は `convert_from_csv_to_json.py` で行う。

| 種別 | オープンデータ | DynamoDB / スキル (`TrashNo`) |
|---|---|---|
| 収集なし | 空欄(NaN) / 0 | 0 |
| 燃やせるごみ | 1 | 1 |
| 燃やせないごみ | 2 | 2 |
| びん・缶・ペット | 8 | 4 |
| 容器プラ | 9 | 3 |
| 雑がみ | 10 | 5 |
| 枝・葉・草 | 11 | 6 |

---

## 4. 既知の落とし穴

- **`batch_insert_to_dynamodb.py` / `delete_all_items.py` / `check_trashno.py` / `insert_dynamodb_production.py` は本番がデフォルト接続先**。ローカル用途では必ず環境変数で切り替え + assert
- `delete_all_items.py` は本番に向いている。**本番では絶対に実行しない**
- `insert_dynamodb_local.py` / `insert_dynamodb_production.py` は旧スクリプト（入力ファイル名固定）。現在は `batch_insert_to_dynamodb.py` を使う
- `convert_from_csv_to_json.py` は 2026-09 に以下を修正済み（コミット 6d6b683）
  - 出力ファイルを追記モード `'a'` で開いていたため、既存 `insert-dynamodb.json` があると壊れた JSON になった → `'w'` に修正
  - `re.sub('\A', ...)` が Python 3.12 で SyntaxWarning → raw 文字列に修正
- CSV は BOM 付き UTF-8。pandas は BOM を除去するので現状問題はないが、列名比較で問題が出たら BOM を疑う
- `put_item` は同一キーを上書きする（エラーにならない）

## 5. オープンデータ構造の過去の変更履歴
- 2020-08: ヘッダが `中央区①` 形式に → ①〜⑦ を数字へ置換するロジック追加
- 2021-09: `曜日` 列名が `曜` に変更
- 2022〜2026: 構造変更なし（2026-09 公開分も 48列・同じ列名・同じ番号体系）

## 6. 実施ログ
| 実施日 | 対象期間 | 件数 | 備考 |
|---|---|---|---|
| 2025-10-01 | 2025-10-01〜2026-09-30 | - | `batch_insert_to_dynamodb.py` 導入 |
| 2026-09-27 | 2026-10-01〜2027-09-30 | 16,790 | 変換スクリプトのバグ修正。本番投入前の既存 184 件（09-27〜09-30）、投入後 16,974 件 |
| 次回 2027-09 | 2027-10-01〜2028-09-30 | 16,836 見込み | **うるう年（366日）** |
