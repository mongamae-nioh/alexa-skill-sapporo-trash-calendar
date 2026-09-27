# SapporoTrashCalendar (Alexa スキル) プロジェクトルール

札幌市のごみ収集日を答える Alexa スキル。データは DynamoDB `SapporoTrashCalendar`（ap-northeast-1）。
スキル本体（`SapporoTrash.py`）は python3 版リポジトリへ移行済みで、このリポジトリの主用途は **年次のごみデータ更新**。

## 作業開始時に読むもの
- 状況: `.claude/plans/project-status.md`
- 年次データ更新をするなら必ず次の Runbook に従う:
  @docs/annual-data-update.md

## 重要な制約
- **本番 DynamoDB のテーブル・アイテムは削除しない。年次更新は追加のみ**（`.claude/adr/0001-production-add-only.md`）
- 多くのスクリプトは **本番がデフォルト接続先**。ローカル操作は `AWS_ENDPOINT_URL_DYNAMODB=http://localhost:8000` を付け、endpoint を assert してから実行（`.claude/adr/0002-local-endpoint-via-env.md`）
- 本番への書き込みは人間の明示的な OK を得てから
- リポジトリは公開（GitHub）。AWS アカウント ID・IAM ユーザー名・認証情報をコミットしない
- `docker/dynamodb/`（DynamoDB Local のデータ）はコミットしない
