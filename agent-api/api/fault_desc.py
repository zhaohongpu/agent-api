from service.fault import *

fault_service = FaultService()

def fault_desc_api(request, socketio, app):
    event_id = request.form.get("event_id", "")
    raw_query = request.form.get("raw_query", "")
    conversation_id = get_conversation_id(request)
    is_send_text = request.form.get("is_send_text", "").lower() == "true"

    logger.info("fault_desc_api conversation_id:{} event_id:{} raw_query".format(conversation_id, event_id, raw_query))

    send_data = json.dumps({"type": "chat", "data": "智能体正在进行故障信息收集..."}, ensure_ascii=False)
    socketio.emit('message', send_data, room=conversation_id)

    fault = fault_service.get_fault(event_id)

    if fault is None:
        api_data = {
            'code': 404,
            'message': '',
            'data': f'没有找到事件ID[{event_id}]对应的故障信息'
        }
        return make_api_response(api_data) #

    text = fault_service.get_desc_text(fault)

    send_data = {
        "type": "fault_desc",
        "data": {
            "images": {
                "gongqu_url": "http://statics-nrxt.dcloud.sh.dc.sgcc.com.cn:1082/GAS/WebPage/business/gas/bigModelChain/dzGraph.html?eventId=" + event_id,
                "user_url": "http://statics-nrxt.dcloud.sh.dc.sgcc.com.cn:1082/GAS/WebPage/business/gas/bigModelChain/vipUser.html?eventId=" + event_id
            }
        }
    }

    send_data = json.dumps(send_data, ensure_ascii=False)
    socketio.emit('message', send_data, room=conversation_id)

    # 故障信息保存，供分析和转供组件使用
    key = "fault_" + conversation_id
    set_cache(key, json.dumps(fault, ensure_ascii=False))

    api_data = {
        'code': 0,
        'message': 'OK',
        'data': text
    }

    if is_send_text:
        send_data = json.dumps({"type": "chat", "data": text}, ensure_ascii=False)
        socketio.emit('message', send_data, room=conversation_id)

    return make_api_response(api_data)  #