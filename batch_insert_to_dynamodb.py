#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import boto3
import json
import sys
from decimal import Decimal

# DynamoDBクライアントを作成
dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1')
table = dynamodb.Table('SapporoTrashCalendar')

def batch_insert(json_file):
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
    if len(sys.argv) != 2:
        print('使用方法: python batch_insert_to_dynamodb.py [JSONファイル]')
        sys.exit(1)

    json_file = sys.argv[1]
    batch_insert(json_file)