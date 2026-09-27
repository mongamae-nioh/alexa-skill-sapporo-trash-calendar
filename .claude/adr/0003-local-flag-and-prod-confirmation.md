# ADR-0003: DynamoDB 操作スクリプトに `--local` フラグと本番確認プロンプトを導入する

- 日付: 2026-09-27
- ステータス: 採用（ADR-0002 を置き換え）

## 背景
ADR-0002 では環境変数 `AWS_ENDPOINT_URL_DYNAMODB` でローカルへ切り替えていたが、付け忘れると本番に書き込む・削除するリスクが残っていた。

## 決定
- `batch_insert_to_dynamodb.py` と `delete_all_items.py` は共通モジュール `dynamodb_target.py` で接続先を決める
- `--local` で DynamoDB Local（`http://localhost:8000`、ダミー認証情報）。実 endpoint が localhost でなければ中断
- フラグなしは本番。実際の endpoint を表示し、`yes` 入力がないと中断。`--yes` で確認を省略できる
- 本番指定なのに endpoint が環境変数等で `amazonaws.com` 以外に向いていたら中断

## 検討した代替案
- デフォルトをローカルにして `--prod` を必須にする: 最も安全だが、既存の本番投入コマンドや過去の README 手順と意味が逆転し、古い手順で「本番に投入したつもりがローカルだった」という逆方向の事故が起きる。本番確認プロンプトで十分な安全性が得られるため不採用

## 帰結
- ローカル操作は `python batch_insert_to_dynamodb.py --local insert-dynamodb.json` だけでよい（環境変数不要）
- Claude が本番投入するときは、人間の OK を得たうえで `--yes` を付ける
