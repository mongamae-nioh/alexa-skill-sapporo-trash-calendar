# Project Status

最終更新: 2026-09-27

## 完了済み
- 本番 DynamoDB に 2026-10-01〜2027-09-30 のデータを投入（16,790件）
- `convert_from_csv_to_json.py` のバグ修正（追記モードによる JSON 破損、SyntaxWarning）
- 年次更新 Runbook 作成（`.claude/docs/annual-data-update.md`）

## 次回予定
- **2027年9月**: 2027-10-01〜2028-09-30 のデータ更新（うるう年 366日 → 16,836件見込み）。Runbook に従う

## 未実施・改善候補
- `batch_insert_to_dynamodb.py` 等に `--local` フラグを追加し、本番誤爆リスクを下げる（人間の判断待ち）
- 変換結果の検証（件数・番号体系）をスクリプト化する
- テストコードは存在しない

## 既知の不具合・注意
- 多くのスクリプトが本番をデフォルト接続先にしている（Runbook「既知の落とし穴」参照）
