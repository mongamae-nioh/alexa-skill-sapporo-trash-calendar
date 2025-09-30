#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import boto3
import sys

# DynamoDBクライアントを作成
# dynamodb = boto3.resource('dynamodb',endpoint_url='http://localhost:8000')
dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1')
table = dynamodb.Table('SapporoTrashCalendar')

# 全アイテムを削除
def delete_all_items():
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
    response = input('本当にすべてのデータを削除しますか？ (yes/no): ')
    if response.lower() == 'yes':
        delete_all_items()
    else:
        print('キャンセルしました。')