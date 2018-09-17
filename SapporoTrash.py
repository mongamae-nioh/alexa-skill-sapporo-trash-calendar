# coding: UTF-8
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_model.ui import SimpleCard
from ask_sdk_core.response_helper import ResponseFactory
from ask_sdk.standard import StandardSkillBuilder
import datetime
import boto3
from boto3.dynamodb.conditions import Key, Attr
dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1')
table = dynamodb.Table('SapporoTrashCalendar')

sb = StandardSkillBuilder(table_name="SapporoTrash", auto_create_table=True)

class LaunchRequestHandler(AbstractRequestHandler):
     def can_handle(self, handler_input):
         return handler_input.request_envelope.request.object_type == "LaunchRequest"

     def handle(self, handler_input):
         attr = handler_input.attributes_manager.persistent_attributes
         if not attr:
             speech_text = "札幌市のゴミ収集情報をお知らせします。はじめに、収集エリアの設定を行います。おすまいの区を教えてください"
             card_title = "初期設定"
             card_body = "お住いの区を教えてください"
             reprompt = "おすまいの区を教えてください"
         else:
             speech_text = "今日以降で何のゴミか知りたい日、または、出したいゴミの種類、どちらかを教えてください"
             reprompt = "今日以降で何のゴミか知りたい日、または、出したいゴミの種類、どちらかを教えてください"
             card_title = "こんな風に話かけてください"
             card_body = "・今日のゴミはなに？\n・燃えないゴミは次いつ？"
             
         handler_input.attributes_manager.session_attributes = attr

         handler_input.response_builder.speak(speech_text).ask(reprompt).set_card(SimpleCard(card_title, card_body)).set_should_end_session(False)
         return handler_input.response_builder.response

class SelectWardIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (handler_input.request_envelope.request.object_type == "IntentRequest"
                and handler_input.request_envelope.request.intent.name == "SelectWardIntent")

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        ward_is = str(slots['ward'].value)
        attr = handler_input.attributes_manager.persistent_attributes
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr['ward'] = ward_is

        if 'ward_calno' in attr:
            speech_text = "今日以降で何のゴミか知りたい日、または、出したいゴミの種類、どちらかを教えてください"
            card_title = "こんな風に話かけてください"
            card_body = "・今日のゴミはなに？\n・燃えないゴミは次いつ？"
            
            handler_input.response_builder.speak(speech_text).set_card(SimpleCard(card_title, card_body)).set_should_end_session(False)
            return handler_input.response_builder.response

        if session_attr['ward'] is not None:
            tellme = "つづいてカレンダー番号を教えてください。カレンダー番号は札幌市から配布された家庭ごみ収集日のカレンダーか、札幌市のウェブサイトで確認できます"
            tellmeagain = "カレンダー番号を教えてください。札幌市、ごみ収集日カレンダー、とウェブで検索すると確認できます"
            card_title = "初期設定"
            card_body = "カレンダー番号を教えてください"

            if ward_is == "中央区" or ward_is == "中央": 
                session_attr['ward_name_alpha'] = "chuo"
                session_attr['ward'] = "中央区"
                speech_text = tellme
                reprompt = tellmeagain
            elif ward_is == "北区" or ward_is == "北":
                session_attr['ward_name_alpha'] = "kita"
                session_attr['ward']  = "北区"
                speech_text = tellme
                reprompt = tellmeagain
            elif ward_is == "南区" or ward_is == "南":
                session_attr['ward_name_alpha'] = "minami"
                session_attr['ward'] = "南区"
                speech_text = tellme
                reprompt = tellmeagain
            elif ward_is == "東区" or ward_is == "東":
                session_attr['ward_name_alpha'] = "higashi"
                session_attr['ward'] = "東区"
                speech_text = tellme
                reprompt = tellmeagain
            elif ward_is == "西区" or ward_is == "西":
                session_attr['ward_name_alpha'] = "nishi"
                session_attr['ward'] = "西区"
                speech_text = tellme
                reprompt = tellmeagain
            elif ward_is == "豊平区" or ward_is == "豊平":
                session_attr['ward_name_alpha'] = "toyohira"
                session_attr['ward'] = "豊平区"
                speech_text = tellme
                reprompt = tellmeagain
            elif ward_is == "厚別区" or ward_is == "厚別":
                session_attr['ward_name_alpha'] = "atsubetsu"
                session_attr['ward'] = "厚別区"
                speech_text = tellme
                reprompt = tellmeagain
            elif ward_is == "清田区" or ward_is == "清田":
                session_attr['ward_name_alpha'] = "kiyota"
                session_attr['ward'] = "清田区"
                speech_text = tellme
                reprompt = tellmeagain
            elif ward_is == "手稲区" or ward_is == "手稲":
                session_attr['ward_name_alpha'] = "teine"
                session_attr['ward'] = "手稲区"
                speech_text = tellme
                reprompt = tellmeagain
            elif ward_is == "白石区" or ward_is == "白石":
                session_attr['ward_name_alpha'] = "shiroishi"
                # しらいし区と発話してしまうため
                session_attr['ward'] = "しろ石区"
                speech_text = tellme
                reprompt = tellmeagain
            else:
                speech_text = "お住まいの、区を教えてください"
                reprompt = "お住まいの、区を教えてください"
                card_title = "初期設定"
                card_body = "お住いの区を教えてください"

            handler_input.response_builder.speak(speech_text).ask(reprompt).set_card(SimpleCard(card_title, card_body)).set_should_end_session(False)
            return handler_input.response_builder.response

class SelectCalendarIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (handler_input.request_envelope.request.object_type == "IntentRequest"
                and handler_input.request_envelope.request.intent.name == "SelectCalendarIntent")

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        calendar_number_is = int(slots['calendar_number'].value)
        attr = handler_input.attributes_manager.persistent_attributes
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr['calendar_number'] = calendar_number_is
        
        if 'ward_calno' in attr:
            speech_text = "今日以降で何のゴミか知りたい日、または、出したいゴミの種類、どちらかを教えてください"
            card_title = "こんな風に話かけてください"
            card_body = "・今日のゴミはなに？\n・燃えないゴミは次いつ？"
            
            handler_input.response_builder.speak(speech_text).set_card(SimpleCard(card_title, card_body)).set_should_end_session(False)
            return handler_input.response_builder.response

        if 'ward_name_alpha' in session_attr:
            tellme = "おすまいは{}、カレンダー番号は{}番です。よろしいですか?".format(session_attr['ward'],session_attr['calendar_number'])

            card_title = "初期設定"
            card_body = "よろしいですか？"

            # 中央区
            if session_attr['ward_name_alpha'] == "chuo" and calendar_number_is >=1 and calendar_number_is <= 6:
                session_attr['calendar_number'] = calendar_number_is
                session_attr['ward_calno'] = session_attr['ward_name_alpha'] + "-" + str(session_attr['calendar_number'])
                speech_text = tellme
            # 北区
            elif session_attr['ward_name_alpha'] == "kita" and calendar_number_is >=1 and calendar_number_is <= 6:
                session_attr['calendar_number'] = calendar_number_is
                session_attr['ward_calno'] = session_attr['ward_name_alpha'] + "-" + str(session_attr['calendar_number'])
                speech_text = tellme
            # 南区
            elif session_attr['ward_name_alpha'] == "minami" and calendar_number_is >=1 and calendar_number_is <= 7:
                session_attr['calendar_number'] = calendar_number_is
                session_attr['ward_calno'] = session_attr['ward_name_alpha'] + "-" + str(session_attr['calendar_number'])
                speech_text = tellme
            # 東区
            elif session_attr['ward_name_alpha'] == "higashi" and calendar_number_is >=1 and calendar_number_is <= 6:
                session_attr['calendar_number'] = calendar_number_is
                session_attr['ward_calno'] = session_attr['ward_name_alpha'] + "-" + str(session_attr['calendar_number'])
                speech_text = tellme
            # 西区
            elif session_attr['ward_name_alpha'] == "nishi" and calendar_number_is >=1 and calendar_number_is <= 4:
                session_attr['calendar_number'] = calendar_number_is
                session_attr['ward_calno'] = session_attr['ward_name_alpha'] + "-" + str(session_attr['calendar_number'])
                speech_text = tellme
            # 豊平区
            elif session_attr['ward_name_alpha'] == "toyohira" and calendar_number_is >=1 and calendar_number_is <= 4:
                session_attr['calendar_number'] = calendar_number_is
                session_attr['ward_calno'] = session_attr['ward_name_alpha'] + "-" + str(session_attr['calendar_number'])
                speech_text = tellme
            # 厚別区
            elif session_attr['ward_name_alpha'] == "atsubetsu" and calendar_number_is >=1 and calendar_number_is <= 4:
                session_attr['calendar_number'] = calendar_number_is
                session_attr['ward_calno'] = session_attr['ward_name_alpha'] + "-" + str(session_attr['calendar_number'])
                speech_text = tellme
            # 清田区
            elif session_attr['ward_name_alpha'] == "kiyota" and calendar_number_is >=1 and calendar_number_is <= 2:
                session_attr['calendar_number'] = calendar_number_is
                session_attr['ward_calno'] = session_attr['ward_name_alpha'] + "-" + str(session_attr['calendar_number'])
                speech_text = tellme
            # 手稲区
            elif session_attr['ward_name_alpha'] == "teine" and calendar_number_is >=1 and calendar_number_is <= 3:
                session_attr['calendar_number'] = calendar_number_is
                session_attr['ward_calno'] = session_attr['ward_name_alpha'] + "-" + str(session_attr['calendar_number'])
                speech_text = tellme
            # 白石区
            elif session_attr['ward_name_alpha'] == "shiroishi" and calendar_number_is >=1 and calendar_number_is <= 4:
                session_attr['calendar_number'] = calendar_number_is
                session_attr['ward_calno'] = session_attr['ward_name_alpha'] + "-" + str(session_attr['calendar_number'])
                speech_text = tellme
            else:
                speech_text = "そのカレンダー番号はありませんでした。ただしい番号を教えてください"
                card_body = "カレンダー番号を教えてください"

        else:
            speech_text = "カレンダー番号を教えてください"
            card_title = "初期設定"
            card_body = "カレンダー番号を教えてください"

        handler_input.response_builder.speak(speech_text).ask(speech_text).set_card(SimpleCard(card_title, card_body)).set_should_end_session(False)
        return handler_input.response_builder.response

class FixIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (handler_input.request_envelope.request.object_type == "IntentRequest"
                and handler_input.request_envelope.request.intent.name == "AMAZON.YesIntent")
      
    def handle(self, handler_input):
        attr = handler_input.attributes_manager.persistent_attributes
        session_attr = handler_input.attributes_manager.session_attributes

        if 'ward_calno' in attr:
            speech_text = "今日以降で何のゴミか知りたい日、または、出したいゴミの種類、どちらかを教えてください"
            card_title = "こんな風に話かけてください"
            card_body = "・今日のゴミはなに？\n・燃えないゴミは次いつ？"
            
            handler_input.response_builder.speak(speech_text).ask(speech_text).set_card(SimpleCard(card_title, card_body)).set_should_end_session(False)
            return handler_input.response_builder.response
            
        if session_attr['ward_calno'] is not None:
            speech_text = "初期設定が完了しました。今日以降で何のゴミか知りたい日、または、出したいゴミの種類、どちらかを教えてください"
            card_title = "こんな風に話かけてください"
            card_body = "・今日のゴミはなに？\n・燃えないゴミは次いつ？"
            
            # セッション情報をpersistentへ書き込み
            handler_input.attributes_manager.persistent_attributes = session_attr
            handler_input.attributes_manager.save_persistent_attributes()
        else:
            speech_text = "初期設定を完了してください。もう一度おすまいの区を教えてください"
            card_title = "初期設定"
            card_body = "お住いの区を教えてください"

        handler_input.response_builder.speak(speech_text).ask(speech_text).set_card(SimpleCard(card_title, card_body)).set_should_end_session(False)
        return handler_input.response_builder.response

class NoIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (handler_input.request_envelope.request.object_type == "IntentRequest"
                and handler_input.request_envelope.request.intent.name == "AMAZON.NoIntent")
      
    def handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        attr = handler_input.attributes_manager.persistent_attributes
        
        if 'ward_calno' in attr:
            speech_text = "今日以降で何のゴミか知りたい日、または、出したいゴミの種類、どちらかを教えてください"
            card_title = "こんな風に話かけてください"
            card_body = "・今日のゴミはなに？\n・燃えないゴミは次いつ？"
            
            handler_input.response_builder.speak(speech_text).ask(speech_text).set_card(SimpleCard(card_title, card_body)).set_should_end_session(False)
            return handler_input.response_builder.response
        
        if not attr:
            session_attr['ward'] = ''
            session_attr['ward_name_alpha'] = ''
            session_attr['calendar_number'] = ''
            session_attr['ward_calno'] = ''
            speech_text = "もう一度、初期設定を行います。お住いの区を教えてください"
            card_title = "初期設定"
            card_body = "お住いの区を教えてください"
            reprompt = "おすまいの区を教えてください"
            
            handler_input.response_builder.speak(speech_text).ask(reprompt).set_card(SimpleCard(card_title, card_body)).set_should_end_session(False)
            return handler_input.response_builder.response

class WhatTrashDayIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (handler_input.request_envelope.request.object_type == "IntentRequest"
                and handler_input.request_envelope.request.intent.name == "WhatTrashDayIntent")

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        date = slots['when'].value
        attr = handler_input.attributes_manager.persistent_attributes
        slicemonth = date[5:7]
        sliceday = date[8:10]
        monthday = str(slicemonth) + "月" + str(sliceday) + "日"

        if not attr:
            speech_text = "はじめに、収集エリアの設定を行います。おすまいの区を教えてください"
            card_title = "初期設定"
            card_body = "お住いの区を教えてください"
            reprompt = "おすまいの区を教えてください"
            
            handler_input.response_builder.speak(speech_text).ask(reprompt).set_card(SimpleCard(card_title, card_body)).set_should_end_session(False)
            return handler_input.response_builder.response

        if attr['ward_calno'] is not None:
            response = table.query(
                KeyConditionExpression=Key('Date').eq(date) & Key('WardCalNo').eq(attr['ward_calno'])
            )

            TrashNo = response['Items'][0]['TrashNo']

            if TrashNo == 1:
                jptrashname = '燃やせるごみ、スプレー缶類'
            elif TrashNo == 2:
                jptrashname = '燃やせないごみ、乾電池、ライター'
            elif TrashNo == 3:
                jptrashname = '容器、プラ'
            elif TrashNo == 4:
                jptrashname = 'びん、缶、ペット'
            elif TrashNo == 5:
                jptrashname = '雑がみ'
            elif TrashNo == 6:
                jptrashname = '枝、葉、くさ'
            elif TrashNo == 0:
                jptrashname = '収集なし'

            speech_text = "{}の日です。".format(jptrashname)

        handler_input.response_builder.speak(speech_text).ask(speech_text).set_card(SimpleCard(monthday, jptrashname)).set_should_end_session(True)
        return handler_input.response_builder.response

class NextWhenTrashDayIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (handler_input.request_envelope.request.object_type == "IntentRequest"
                and handler_input.request_envelope.request.intent.name == "NextWhenTrashDayIntent")
      
    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        trash = slots['trash'].value
        attr = handler_input.attributes_manager.persistent_attributes
        
        if not attr:
            speech_text = "はじめに、収集エリアの設定を行います。おすまいの区を教えてください"
            card_title = "初期設定"
            card_body = "お住いの区を教えてください"
            reprompt = "おすまいの区を教えてください"
            
            handler_input.response_builder.speak(speech_text).ask(reprompt).set_card(SimpleCard(card_title, card_body)).set_should_end_session(False)
            return handler_input.response_builder.response

        if attr['ward_calno'] is not None:
            # 燃やせるゴミ
            if trash == '燃やせる' or trash == '燃える' or trash == '燃やせるゴミ' or trash == '燃えるゴミ' or trash == '可燃物' or trash == '可燃' or trash == '燃やせるごみ' or trash == '燃えるごみ':
                TrashNo = 1
            # 燃やせないゴミ,乾電池、ライター
            if trash == '燃やせない' or trash == '燃えない' or trash == '燃やせないゴミ' or trash == '燃えないゴミ' or trash == '不燃物' or trash == '不燃' or trash == '電池' or trash == '乾電池' or trash == 'ライター'or trash == '燃やせないごみ' or trash == '燃えないごみ':
                TrashNo = 2
            # プラ
            if trash == 'プラ' or trash == 'プラ容器' or trash == 'プラスチック' or trash == 'プラスティック' or trash == 'プラゴミ' or trash == '発泡スチロール' or trash == '発泡':
                TrashNo = 3
            # ビン、カン、ペット
            if trash == 'ペット' or trash == 'ペットボトル' or trash == 'びん' or trash == '缶' or trash == '空き缶' or trash == 'スチール缶' or trash == 'アルミ缶':
                TrashNo = 4
            # 雑がみ
            if trash == '雑がみ' or trash == '紙' or trash == '包装紙' or trash == '模造紙' or trash == 'レシート' or trash == '箱':
                TrashNo = 5
            # 枝、葉、草
            if trash == '枝' or trash == '葉っぱ' or trash == '葉' or trash == '草' or trash == '雑草' or trash == '枝葉':
                TrashNo = 6

        response = table.query(
            KeyConditionExpression=Key('WardCalNo').eq(attr['ward_calno']),
            FilterExpression=Attr('TrashNo').eq(TrashNo))

        when = response['Items'][0]['Date']
        slicemonth = when[5:7]
        sliceday = when[8:10]
        monthday = str(slicemonth) + "月" + str(sliceday) + "日"
        
        date = datetime.datetime.strptime(when, '%Y-%m-%d')
        weekday = date.strftime("%A")
        if weekday == "Sunday":
            youbi = "日曜日"
        elif weekday == "Monday":
            youbi = "月曜日"
        elif weekday == "Tuesday":
            youbi = "火曜日"
        elif weekday == "Wednesday":
            youbi = "水曜日"
        elif weekday == "Thursday":
            youbi = "木曜日"
        elif weekday == "Friday":
            youbi = "金曜日"
        elif weekday == "Saturday":
            youbi = "土曜日"
        
        TrashNo = response['Items'][0]['TrashNo']
            
        if TrashNo == 1:
            jptrashname = '燃やせるごみ、スプレー缶類'
        elif TrashNo == 2:
            jptrashname = '燃やせないごみ、乾電池、ライター'
        elif TrashNo == 3:
            jptrashname = '容器プラ'
        elif TrashNo == 4:
            jptrashname = 'びん、缶、ペット'
        elif TrashNo == 5:
            jptrashname = '雑がみ'
        elif TrashNo == 6:
            jptrashname = '枝、葉、くさ'

        speech_text = "次の{}は、{}、{}です。".format(jptrashname, monthday, youbi)

        handler_input.response_builder.speak(speech_text).set_card(SimpleCard(jptrashname, monthday)).set_should_end_session(True)
        return handler_input.response_builder.response

class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (handler_input.request_envelope.request.object_type == "IntentRequest"
                and handler_input.request_envelope.request.intent.name == "AMAZON.HelpIntent")

    def handle(self, handler_input):
        speech_text = "お住まいの地域の、ゴミの収集情報をお知らせします。たとえば、今日のゴミはなに？もしくは、次の燃えないゴミはいつ？と聞いてください"
        reprompt = "たとえば、今日のゴミはなに？もしくは、次の燃えないゴミはいつ？と聞いてください"
        card_title = "こんな風に話かけてください"
        card_body = "・今日のゴミはなに？\n・燃えないゴミは次いつ？"
        
        handler_input.response_builder.speak(speech_text).ask(reprompt).set_card(SimpleCard(card_title, card_body)).set_should_end_session(False)
        return handler_input.response_builder.response
        
class CancelAndStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (handler_input.request_envelope.request.object_type == "IntentRequest"
            and (handler_input.request_envelope.request.intent.name == "AMAZON.CancelIntent"
                 or handler_input.request_envelope.request.intent.name == "AMAZON.StopIntent"))

    def handle(self, handler_input):
        speech_text = "いつでもよんでください"

        handler_input.response_builder.speak(speech_text).set_should_end_session(True)
        return handler_input.response_builder.response

class SessionEndedRequestHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        return handler_input.request_envelope.request.object_type == "SessionEndedRequest"

    def handle(self, handler_input):
        #any cleanup logic goes here

        return handler_input.response_builder.response


from ask_sdk_core.dispatch_components import AbstractExceptionHandler

class AllExceptionHandler(AbstractExceptionHandler):

    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):

        # Log the exception in CloudWatch Logs
        print(exception)
        
        speech = "すみません、わかりませんでした。もう一度言ってください。"
        handler_input.response_builder.speak(speech).ask(speech)
        return handler_input.response_builder.response

sb.request_handlers.extend([
    LaunchRequestHandler(),
    SelectWardIntentHandler(),
    SelectCalendarIntentHandler(),
    FixIntentHandler(),
    NoIntentHandler(),
    WhatTrashDayIntentHandler(),
    NextWhenTrashDayIntentHandler(),
    HelpIntentHandler(),
    CancelAndStopIntentHandler(),
    SessionEndedRequestHandler()])

sb.add_exception_handler(AllExceptionHandler())

handler = sb.lambda_handler()