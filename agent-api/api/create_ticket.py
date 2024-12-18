from common import set_cache, get_cache, get_path, get_conversation_id, to_json, logger, make_api_response
from flask import make_response
from third.taihao.api import create_ticket
import json


def create_ticket_api(request, socketio, app):
    conversation_id = get_conversation_id(request)
    raw_query = request.form.get('raw_query', '')

    logger.info("create_ticket_api conversation_id:%s raw_query:%s", conversation_id, raw_query)

    ticket_generated = False
    # 全停
    key = "plan_nn_" + conversation_id
    plan = get_cache(key, return_json=True)
    if plan is not None:
        send_data = {"type": "chat", "data": "正在进行全停故障处置操作票生成中..."}
        socketio.emit('message', to_json(send_data), room=conversation_id)

        plan = plan['data']
        ticket_data = create_ticket(plan, type="nn")

        key = "ticket_nn_" + conversation_id
        set_cache(key, ticket_data)

        ticket_id = ticket_data["content"]["czpid"]
        send_data = {
            "type": "ticket",
            "data": {
                "ticket_type": "n_n",
                "ticket_info": ticket_data["content"],
                "image": "http://10.130.16.194:8000/netorder/otherPage/gis.jsp?ticketId=" + ticket_id
            }
        }
        socketio.emit('message', to_json(send_data), room=conversation_id)
        ticket_generated = True

    # 重载
    key = "plan_n1_" + conversation_id
    plan = get_cache(key, return_json=True)
    if plan is not None:
        send_data = {"type": "chat", "data": "正在进行重载处置操作票生成中..."}
        socketio.emit('message', to_json(send_data), room=conversation_id)

        plan = plan['data']
        plan['cmdType'] = "2"  # N-1
        ticket_data = create_ticket(plan, type="n1")

        key = "ticket_n1_" + conversation_id
        set_cache(key, ticket_data)

        ticket_id = ticket_data["content"]["czpid"]
        send_data = {
            "type": "ticket",
            "data": {
                "ticket_type": "n_1",
                "ticket_info": ticket_data["content"],
                "image": "http://10.130.16.194:8000/netorder/otherPage/gis.jsp?ticketId=" + ticket_id
            }
        }
        socketio.emit('message', to_json(send_data), room=conversation_id)
        ticket_generated = True

    # 单电源
    key = "plan_single_" + conversation_id
    plan = get_cache(key, return_json=True)
    if plan is not None:
        send_data = {"type": "chat", "data": "正在进行单电源处置操作票生成中..."}
        socketio.emit('message', to_json(send_data), room=conversation_id)

        plan['cmdType'] = "3"  # 单电源
        ticket_data = create_ticket(plan, type="single")

        key = "ticket_single_" + conversation_id
        set_cache(key, ticket_data)

        ticket_id = ticket_data["content"]["czpid"]
        send_data = {
            "type": "ticket",
            "data": {
                "ticket_type": "single",
                "ticket_info": ticket_data["content"],
                "image": "http://10.130.16.194:8000/netorder/otherPage/gis.jsp?ticketId=" + ticket_id
            }
        }
        socketio.emit('message', to_json(send_data), room=conversation_id)
        ticket_generated = True
    # 操作票生成结束

    if not ticket_generated:
        result = {"code": 0, "message": "OK", "data": "本次无操作票生成"}
    else:
        result = {"code": 0, "message": "OK", "data": "操作票已全部生成完成"}

    return make_api_response(result)