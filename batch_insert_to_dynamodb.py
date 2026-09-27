#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from decimal import Decimal

from dynamodb_target import build_parser, get_table

def batch_insert(table, json_file):
    # JSONファイルを読み込む
    with open(json_file, 'r', encoding='utf-8') as f:
        items = json.load(f)

    # バッチ処理でインサート（25件ずつ）
    count = 0
    with table.batch_writer() as batch:
        for item in items:
            # TrashNoをDecimalに変換（DynamoDBの仕様）
            item['TrashNo'] = Decimal(str(item['TrashNo']))
            batch.put_item(Item=item)
            count += 1
            if count % 100 == 0:
                print(f'インサート済み: {count}件')

    print(f'合計 {count} 件のアイテムをインサートしました。')

if __name__ == '__main__':
    parser = build_parser('JSONファイルのアイテムを DynamoDB へインサートする（指定なしは本番）')
    parser.add_argument('json_file', help='convert_from_csv_to_json.py で作成した JSON ファイル')
    args = parser.parse_args()

    table = get_table(args, f'{args.json_file} のインサート')
    batch_insert(table, args.json_file)
