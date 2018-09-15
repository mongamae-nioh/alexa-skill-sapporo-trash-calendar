# coding: UTF-8
import sys, codecs
import boto3
from boto3.dynamodb.conditions import Key, Attr
#dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1')
dynamodb = boto3.resource('dynamodb',endpoint_url='http://localhost:8000')
table = dynamodb.Table('SapporoTrashCalendar')

# ここへエリアと日付入力
date = "2018-10-08"
wardcalno = "nishi-2"

response = table.query(
    KeyConditionExpression=Key('Date').eq(date) & Key('WardCalNo').eq(wardcalno))


Count = response['Count']
TrashNo = response['Items'][0]['TrashNo']

if TrashNo == 1:
    jptrashname = '燃やせるごみ'
elif TrashNo == 2:
    jptrashname = '燃やせないごみ'
elif TrashNo == 3:
    jptrashname = '容器プラ'
elif TrashNo == 4:
    jptrashname = 'びん、缶、ペット'
elif TrashNo == 5:
    jptrashname = '雑がみ'
elif TrashNo == 6:
    jptrashname = '枝・葉・草'
else:
    jptrashname = '収集なし'

speech_text = "{}です".format(jptrashname)

print speech_text