# `--local` フラグ追加（本番誤爆防止）

日付: 2026-09-27 / 関連: ADR-0002, ADR-0003

## 目的
環境変数の付け忘れで、ローカルのつもりの書き込み・削除が本番 DynamoDB に向かうリスクを下げる。

## 方針
- 共通モジュール `dynamodb_target.py` に接続先の決定と本番確認を集約
  - `--local`: `http://localhost:8000` + ダミー認証情報。実 endpoint が localhost でなければ中断
  - 指定なし: 本番（ap-northeast-1）。実際の endpoint を表示し `yes` 入力で続行。`--yes` で確認省略（人間の OK 取得後に Claude が使う）
  - 本番指定なのに `AWS_ENDPOINT_URL_DYNAMODB` 等で endpoint が上書きされている場合は中断（表示と実際の食い違い防止）
- 対象: `batch_insert_to_dynamodb.py`（年次投入で使用）、`delete_all_items.py`（最も危険）
- 既存の本番投入コマンド（引数 JSON のみ）は確認プロンプトが増える以外は互換

## TODO
- [x] 計画・ADR 作成
- [x] `dynamodb_target.py` 実装
- [x] `batch_insert_to_dynamodb.py` に適用
- [x] `delete_all_items.py` に適用
- [x] テスト作成・実行（`tests/test_dynamodb_target.py`）
- [x] DynamoDB Local で実動作確認（`--local` 投入、本番確認プロンプトで no → 中断）
- [x] Runbook / README / ADR-0002 / project-status 更新
- [x] コミット
