# -*- coding: utf-8 -*-
# dynamodb_target.py のテスト（ネットワークには接続しない）
# 実行: python -m pytest tests

import argparse
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import dynamodb_target as dt  # noqa: E402


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    # 実行環境の endpoint 上書き・認証情報に影響されないようにする
    for key in ('AWS_ENDPOINT_URL', 'AWS_ENDPOINT_URL_DYNAMODB'):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv('AWS_ACCESS_KEY_ID', 'test')
    monkeypatch.setenv('AWS_SECRET_ACCESS_KEY', 'test')


def args(*argv):
    return dt.build_parser('test').parse_args(list(argv))


def endpoint(resource):
    return resource.meta.client.meta.endpoint_url


def test_default_is_production():
    a = args()
    assert a.local is False and a.yes is False
    assert endpoint(dt.create_resource(a.local)) == 'https://dynamodb.ap-northeast-1.amazonaws.com'


def test_local_flag_targets_dynamodb_local():
    assert endpoint(dt.create_resource(args('--local').local)) == 'http://localhost:8000'


def test_local_flag_wins_over_env_endpoint(monkeypatch):
    monkeypatch.setenv('AWS_ENDPOINT_URL_DYNAMODB', 'https://dynamodb.ap-northeast-1.amazonaws.com')
    assert endpoint(dt.create_resource(True)) == 'http://localhost:8000'


def test_production_rejected_when_env_points_elsewhere(monkeypatch):
    # 本番のつもりが環境変数でローカルに向いている → 食い違いとして中断
    monkeypatch.setenv('AWS_ENDPOINT_URL_DYNAMODB', 'http://localhost:8000')
    with pytest.raises(RuntimeError):
        dt.get_table(args('--yes'), 'test')


def test_validate_endpoint():
    dt.validate_endpoint('http://localhost:8000', local=True)
    dt.validate_endpoint('https://dynamodb.ap-northeast-1.amazonaws.com', local=False)
    with pytest.raises(RuntimeError):
        dt.validate_endpoint('https://dynamodb.ap-northeast-1.amazonaws.com', local=True)
    with pytest.raises(RuntimeError):
        dt.validate_endpoint('http://localhost:8000', local=False)


@pytest.mark.parametrize('answer,expected', [('yes', True), (' YES \n', True), ('no', False), ('', False), ('y', False)])
def test_confirm_production(answer, expected):
    assert dt.confirm_production('x', 'e', input_func=lambda _: answer) is expected


def test_production_cancel_exits_without_table():
    with pytest.raises(SystemExit) as e:
        dt.get_table(args(), 'test', input_func=lambda _: 'no')
    assert e.value.code == 1


def test_production_confirmed_returns_table():
    table = dt.get_table(args(), 'test', input_func=lambda _: 'yes')
    assert table.name == 'SapporoTrashCalendar'


def test_production_yes_flag_skips_prompt():
    def fail(_):
        raise AssertionError('prompt should not be shown')
    assert dt.get_table(args('--yes'), 'test', input_func=fail).name == 'SapporoTrashCalendar'


def test_local_never_prompts():
    def fail(_):
        raise AssertionError('prompt should not be shown')
    assert endpoint(dt.get_table(args('--local'), 'test', input_func=fail)) == 'http://localhost:8000'
