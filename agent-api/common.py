import datetime
import json
import logging
import os
from flask import make_response
from logging import handlers
import time


def make_api_response(api_data):
    if isinstance(api_data, dict):
        api_data = json.dumps(api_data, ensure_ascii=False)

    response = make_response(api_data)
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response


def is_mock_conversation_id():
    return os.getenv("MOCK_CONVERSATION_ID") == '1'


def is_mock_third_api():
    return os.getenv("MOCK_THIRD_API") == '1'


def get_conversation_id(request):
    if is_mock_conversation_id():
        return 'default'

    conversation_id = request.form.get('conversation_id', request.headers.get('Conversation-Id', "default"))
    return conversation_id

def get_optimize_turn(request):
    try:
        turn = int(request.form.get('turn', '1'))
        max_optimize_turn = int(os.getenv('MAX_OPTIMIZE_TURN', '4'))
        if turn >= 1 and turn <= max_optimize_turn:
            return turn
        else:
            return 1
    except Exception as e:
        return 1

def check_weight_number(number):
    try:
        number = int(number)
        if number >= 0 and number <= 100:
            return number
        else:
            return 80
    except Exception as e:
        return 80



def set_consumer_log(text):
    with open(get_path('/log/consumer.log'), 'a') as f:
        now = datetime.datetime.now()
        datetime_str = now.strftime('%Y-%m-%d %H:%M:%S')
        text = "[%s] %s\n" % (datetime_str, text)
        f.write(text)


def get_path(file=''):
    current_dir = os.path.dirname(os.path.abspath(__file__)) + file
    return current_dir


def set_cache(key, data):
    file_name = get_path("/data/cache/" + key + ".json")

    if isinstance(data, dict):
        data = json.dumps(data, ensure_ascii=False)

    with open(file_name, "w") as f:
        f.write(data)


def get_cache(key, return_json=False):
    try:
        file_name = get_path("/data/cache/" + key + ".json")
        if not os.path.exists(file_name):
            return None

        with open(file_name, "r", encoding='utf-8') as f:
            result = f.read()

        if return_json:
            result = json.loads(result)

        return result
    except Exception as e:
        return None


def get_file(file_name, return_json=False):
    file_name = get_path(file_name)
    if not os.path.exists(file_name):
        return None

    with open(file_name, "r") as f:
        result = f.read()

    if return_json:
        result = json.loads(result)

    return result


def to_json(dict_obj):
    if isinstance(dict_obj, str):
        return dict_obj

    return json.dumps(dict_obj, ensure_ascii=False)

def del_kv_info(str):
    if not str:
        return str

    str = str.lower()
    if 'kv' in str:
        str = str.split('kv')[1]
        if '.' in str:
            str = str.split('.')[1]

    return str


def del_cache(key):
    file_name = get_path("/data/cache/" + key + ".json")
    if os.path.exists(file_name):
        os.remove(file_name)

logging.Formatter.converter = time.gmtime

logger = logging.getLogger()

def set_logger():
    formatter = logging.Formatter(
        '%(asctime)s - %(thread)d - %(levelname)s - %(module)s - %(filename)s - %(lineno)d - %(message)s'
    )

    file_handler_info = handlers.TimedRotatingFileHandler(filename=get_path('/log/app.log'),
                                                          when='d',  # 时间单位，周：w；天:d；时: h；分：m；秒: s
                                                          interval=1,  # 间隔多久切一个
                                                          backupCount=100,  # 备份日志保留个数，多余自动删除
                                                          encoding='utf-8')

    file_handler_info.setLevel(logging.DEBUG)
    file_handler_info.setFormatter(formatter)

    file_handler_error = handlers.TimedRotatingFileHandler(filename=get_path('/log/app.log.wf'),
                                                           when='d',  # 时间单位，周：w；天:d；时: h；分：m；秒: s
                                                           interval=1,  # 间隔多久切一个
                                                           backupCount=100,  # 备份日志保留个数，多余自动删除
                                                           encoding='utf-8')
    file_handler_error.setLevel(logging.ERROR)
    file_handler_error.setFormatter(formatter)

    logger.addHandler(file_handler_info)
    logger.addHandler(file_handler_error)
    logger.setLevel(logging.INFO)


set_logger()
