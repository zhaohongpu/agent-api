import time

from common import set_cache, get_cache, get_path, get_conversation_id, logger, make_api_response
from flask import make_response
import json


def exec_ticket_api(request, socketio, app):
    conversation_id = get_conversation_id(request)
    raw_query = request.form.get('raw_query', '')

    logger.info("exec_ticket_api conversation_id:%s raw_query:%s", conversation_id, raw_query)

    # 全停操作票
    key = "ticket_nn_" + conversation_id
    ticket_data = get_cache(key, return_json=True)
    if ticket_data is not None:
        send_data = json.dumps({"type": "chat", "data": "全停方案操作票已下发..."}, ensure_ascii=False)
        socketio.emit('message', send_data, room=conversation_id)

        send_data = {
            "type": "exec_ticket",
            "data": {
                "ticket_type": "n_n",
                "ticket_id": ticket_data["content"]["czpid"],
            }
        }
        send_data = json.dumps(send_data, ensure_ascii=False)
        socketio.emit('message', send_data, room=conversation_id)

        time.sleep(1)

    # 重载操作票

    key = "ticket_n1_" + conversation_id
    ticket_data = get_cache(key, return_json=True)
    if ticket_data is not None:
        send_data = json.dumps({"type": "chat", "data": "重载方案操作票已下发..."}, ensure_ascii=False)
        socketio.emit('message', send_data, room=conversation_id)

        send_data = {
            "type": "exec_ticket",
            "data": {
                "ticket_type": "n_1",
                "ticket_id": ticket_data["content"]["czpid"],
            }
        }
        send_data = json.dumps(send_data, ensure_ascii=False)
        socketio.emit('message', send_data, room=conversation_id)
        time.sleep(1)

    # 单电源操作票
    key = "ticket_single_" + conversation_id
    ticket_data = get_cache(key, return_json=True)

    if ticket_data is not None:
        send_data = json.dumps({"type": "chat", "data": "单电源方案操作票已下发..."}, ensure_ascii=False)
        socketio.emit('message', send_data, room=conversation_id)

        send_data = {
            "type": "exec_ticket",
            "data": {
                "ticket_type": "single",
                "ticket_id": ticket_data["content"]["czpid"],
            }
        }
        send_data = json.dumps(send_data, ensure_ascii=False)
        socketio.emit('message', send_data, room=conversation_id)

    result = {"code": 0, "message": "OK", "data": "网络令已下发，请持续关注指令执行情况。"}
    return make_api_response(result) #
