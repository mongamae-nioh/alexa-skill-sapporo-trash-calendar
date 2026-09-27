#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dynamodb_target import build_parser, get_table

# 全アイテムを削除
def delete_all_items(table):
    # テーブルをスキャン
    scan = table.scan()
    count = 0

    # 各アイテムを削除
    with table.batch_writer() as batch:
        for item in scan['Items']:
            batch.delete_item(
                Key={
                    'WardCalNo': item['WardCalNo'],
                    'Date': item['Date']
                }
            )
            count += 1
            if count % 100 == 0:
                print(f'削除済み: {count}件')

    # ページネーションの処理
    while 'LastEvaluatedKey' in scan:
        scan = table.scan(ExclusiveStartKey=scan['LastEvaluatedKey'])
        with table.batch_writer() as batch:
            for item in scan['Items']:
                batch.delete_item(
                    Key={
                        'WardCalNo': item['WardCalNo'],
                        'Date': item['Date']
                    }
                )
                count += 1
                if count % 100 == 0:
                    print(f'削除済み: {count}件')

    print(f'合計 {count} 件のアイテムを削除しました。')

if __name__ == '__main__':
    # 本番の場合は get_table 内で確認プロンプトが出る
    args = build_parser('テーブルの全アイテムを削除する（指定なしは本番。本番では通常使わない）').parse_args()
    table = get_table(args, '全アイテムの削除')
    delete_all_items(table)