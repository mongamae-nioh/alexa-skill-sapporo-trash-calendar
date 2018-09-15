from __future__ import print_function # Python 2/3 compatibility
import boto3
import json

dynamodb = boto3.resource('dynamodb',endpoint_url='http://localhost:8000')
#dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1')
table = dynamodb.Table('SapporoTrashCalendar')

with open("insert-dynamodb.json") as json_file:
    trash = json.load(json_file)
    with table.batch_writer(overwrite_by_pkeys=['WardCalNo', 'Date']) as batch:
        for i in trash:
            wardcalno = i['WardCalNo']
            date = i['Date']
            trashno = i['TrashNo']
            
            batch.put_item(
                Item={
                    'WardCalNo': wardcalno,
                    'Date': date,
                    'TrashNo': trashno
                    
                }
            )