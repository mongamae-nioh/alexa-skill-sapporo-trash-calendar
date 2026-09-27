# ADR-0002: ローカル/本番の接続先は環境変数 `AWS_ENDPOINT_URL_DYNAMODB` で切り替える

- 日付: 2026-09-27
- ステータス: 採用（暫定。スクリプトへのフラグ追加は未実施）

## 背景
`batch_insert_to_dynamodb.py` など多くのスクリプトは `boto3.resource('dynamodb', region_name='ap-northeast-1')` で
本番に接続するようハードコードされている。過去はコメントアウトの付け替えでローカルと切り替えていた。

## 決定
コードは変更せず、ローカル操作時は以下を付けて実行する。
```
AWS_ENDPOINT_URL_DYNAMODB=http://localhost:8000 AWS_ACCESS_KEY_ID=dummy AWS_SECRET_ACCESS_KEY=dummy AWS_DEFAULT_REGION=ap-northeast-1
```
さらに実行直前に `meta.endpoint_url == 'http://localhost:8000'` を assert する。

## 理由
- boto3 1.28 以降はサービス別 endpoint を環境変数で上書きできるため、コード改修なしでローカルに向けられる
- コメント付け替え方式は戻し忘れで本番に誤爆するリスクがある

## 残課題
- 環境変数の付け忘れで本番に書き込むリスクは残る。`--local` フラグ追加などのコード改修は人間の判断待ち
