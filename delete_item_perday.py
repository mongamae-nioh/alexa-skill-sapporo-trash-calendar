# coding: UTF-8
import datetime
import boto3
dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1')
#dynamodb = boto3.resource('dynamodb',endpoint_url='http://localhost:8000')
table = dynamodb.Table('SapporoTrashCalendar')

yesterday = datetime.date.today() - datetime.timedelta(1)
yesterday = yesterday.strftime("%Y-%m-%d")

wardtaple = ('chuo-1','chuo-2','chuo-3','chuo-4','chuo-5','chuo-6',
             'higashi-1','higashi-2','higashi-3','higashi-4','higashi-5','higashi-6',
             'nishi-1','nishi-2','nishi-3','nishi-4',
             'minami-1','minami-2','minami-3','minami-4','minami-5','minami-6','minami-7',
             'kita-1','kita-2','kita-3','kita-4','kita-5','kita-6',
             'toyohira-1','toyohira-2','toyohira-3','toyohira-4',
             'atsubetsu-1','atsubetsu-2','atsubetsu-3','atsubetsu-4',
             'kiyota-1','kiyota-2',
             'teine-1','teine-2','teine-3',
             'shiroishi-1','shiroishi-2','shiroishi-3','shiroishi-4',
             )

# 全収集エリアの昨日の項目を削除
def lambda_handler(event, context):
    for i in wardtaple:
        response = table.delete_item(
            Key={
                'WardCalNo': i,
                'Date': yesterday
            }
        ) 
