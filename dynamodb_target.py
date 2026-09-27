#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# DynamoDB の接続先（ローカル / 本番）を決める共通モジュール
# 本番への誤爆を防ぐため、本番は確認プロンプトを通さないと操作できない

import argparse
import sys

import boto3

TABLE_NAME = 'SapporoTrashCalendar'
REGION = 'ap-northeast-1'
LOCAL_ENDPOINT = 'http://localhost:8000'


def add_target_arguments(parser):
    parser.add_argument('--local', action='store_true',
                        help=f'DynamoDB Local ({LOCAL_ENDPOINT}) を操作する。指定しない場合は本番')
    parser.add_argument('--yes', action='store_true',
                        help='本番操作時の確認プロンプトを省略する')
    return parser


def create_resource(local):
    if local:
        # DynamoDB Local (-sharedDb) は認証情報を検証しないのでダミーでよい
        return boto3.resource('dynamodb', endpoint_url=LOCAL_ENDPOINT, region_name=REGION,
                              aws_access_key_id='dummy', aws_secret_access_key='dummy')
    return boto3.resource('dynamodb', region_name=REGION)


def validate_endpoint(endpoint_url, local):
    # 実際の接続先がフラグの意図と食い違っていたら例外
    # (例: 本番指定なのに AWS_ENDPOINT_URL_DYNAMODB でローカルに向いている)
    if local and endpoint_url != LOCAL_ENDPOINT:
        raise RuntimeError(f'--local 指定ですが接続先が {endpoint_url} です')
    if not local and 'amazonaws.com' not in endpoint_url:
        raise RuntimeError(f'本番指定ですが接続先が {endpoint_url} です。'
                           f'AWS_ENDPOINT_URL_DYNAMODB 等の環境変数を外すか --local を付けてください')


def confirm_production(action, endpoint_url, input_func=input):
    answer = input_func(f'本番 DynamoDB ({endpoint_url}) の {TABLE_NAME} に対して「{action}」を実行します。'
                        f'続行しますか？ (yes/no): ')
    return answer.strip().lower() == 'yes'


def get_table(args, action, input_func=input):
    """引数に従って Table を返す。本番で確認が得られなければ終了する"""
    dynamodb = create_resource(args.local)
    endpoint_url = dynamodb.meta.client.meta.endpoint_url
    validate_endpoint(endpoint_url, args.local)

    print(f'接続先: {endpoint_url} ({"ローカル" if args.local else "本番"})')
    if not args.local and not args.yes:
        if not confirm_production(action, endpoint_url, input_func):
            print('キャンセルしました。')
            sys.exit(1)

    return dynamodb.Table(TABLE_NAME)


def build_parser(description):
    return add_target_arguments(argparse.ArgumentParser(description=description))
