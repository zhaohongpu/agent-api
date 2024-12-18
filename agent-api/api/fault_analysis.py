from service.fault import *

fault_service = FaultService()

def fault_analysis_api(request, socketio, app):
    conversation_id = get_conversation_id(request)  # 会话ID，用于串联数据
    raw_query = request.form.get('raw_query', '')

    logger.info("fault_analysis_api conversation_id:%s raw_query:%s", conversation_id, raw_query)

    key = "fault_" + conversation_id
    fault = get_cache(key, return_json=True)
    if fault is None:
        api_data = {
            'code': 404,
            'message': '',
            'data': '没有找到相应的故障信息'
        }
        return make_api_response(api_data)


    send_data = json.dumps({"type": "chat", "data": "智能体正在进行故障分析..."}, ensure_ascii=False)
    socketio.emit('message', send_data, room=conversation_id)

    text = fault_service.get_analysis_text(fault)

    send_data = {
        "type": "fault_analysis",
        "data": {
            "text": text['send_text'],
        }
    }

    send_data = json.dumps(send_data, ensure_ascii=False)
    socketio.emit('message', send_data, room=conversation_id)

    api_data = {
        "code": 0,
        "message": 'OK',
        "data": text['api_text']
    }

    return make_api_response(api_data) #