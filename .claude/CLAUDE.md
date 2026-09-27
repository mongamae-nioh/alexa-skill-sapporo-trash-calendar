# SapporoTrashCalendar (Alexa スキル) プロジェクトルール

札幌市のごみ収集日を答える Alexa スキル。データは DynamoDB `SapporoTrashCalendar`（ap-northeast-1）。
スキル本体（`SapporoTrash.py`）は python3 版リポジトリへ移行済みで、このリポジトリの主用途は **年次のごみデータ更新**。

## 作業開始時に読むもの
- 状況: `.claude/plans/project-status.md`
- 年次データ更新をするなら必ず次の Runbook に従う:
  @docs/annual-data-update.md

## 重要な制約
- **本番 DynamoDB のテーブル・アイテムは削除しない。年次更新は追加のみ**（`.claude/adr/0001-production-add-only.md`）
- **DynamoDB に書き込む・削除するスクリプトを実行する前に、接続先（コード上の endpoint とランタイムの実際の endpoint）の両方を確認する**。多くのスクリプトは本番がデフォルト接続先
  - `batch_insert_to_dynamodb.py` / `delete_all_items.py` はローカル操作時 `--local` を付ける。フラグなしは本番（確認プロンプト、`--yes` で省略）（`.claude/adr/0003-local-flag-and-prod-confirmation.md`）
  - 新しく DB 操作スクリプトを作るときは `dynamodb_target.py` を使う
- テスト: `python -m pytest tests -q`
- 本番への書き込みは人間の明示的な OK を得てから
- リポジトリは公開（GitHub）。AWS アカウント ID・IAM ユーザー名・認証情報をコミットしない
- `docker/dynamodb/`（DynamoDB Local のデータ）はコミットしない
