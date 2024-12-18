from ban_or_enforced import is_ban_or_enforced
from common import get_optimize_turn, set_cache, get_cache, get_file, get_conversation_id, logger, is_mock_third_api, make_api_response, to_json
from service.plan import PlanOptimizeService, PlanService
from third.zheda.parser import get_plan_nn_info
from third.dfe.api import post_plan_info
import json


def optimize_plan_nn_v2_api(request, socketio, app):
    conversation_id = get_conversation_id(request)
    raw_query = request.form.get('raw_query', '')

    ori_turn = request.form.get('turn', '')
    turn = get_optimize_turn(request)

    conclusionText = request.form.get('conclusionText', '')
    conclusionTwoText = request.form.get('conclusionTwoText', '')
    score = float(request.form.get('score', '0'))

    subName = request.form.get('subName', '')
    subId = PlanService.get_station_id(subName)

    busbarNotRepeatLineList, busbarRepeatLineList = is_ban_or_enforced(raw_query, subName)

    disableDev = request.form.get('disableDev', '')
    isYaoKong = request.form.get('isYaoKong', '').lower() == 'true'
    userNumberWeight = int(request.form.get('userNumberWeight', '100'))
    lineLoadRateThreshold = int(request.form.get('lineLoadRateThreshold', '80'))
    isBusBarRecover = request.form.get('isBusBarRecover', '').lower() == 'true'

    # 故障信息
    key = "fault_" + conversation_id
    fault = get_cache(key, return_json=True)
    fault_time = fault['fault_list'][0]['fault_sec'] if fault is not None else None

    input = {
        "ori_turn": ori_turn,
        "turn": turn,
        "conclusionText": conclusionText,
        "conclusionTwoText": conclusionTwoText,
        "score": score,
        "subName": subName,
        "subId": subId,
        "isYaoKong": isYaoKong,
        "userNumberWeight": userNumberWeight,
        "lineLoadRateThreshold": lineLoadRateThreshold,
        "isBusBarRecover": isBusBarRecover,
        "disableDev": disableDev,
        "busbarNotRepeatLineList": busbarNotRepeatLineList,
        "busbarRepeatLineList": busbarRepeatLineList
    }

    if busbarNotRepeatLineList or busbarRepeatLineList:
        for busbar_info in busbarNotRepeatLineList + busbarRepeatLineList:
            if any(busbar_info.get(key) == 'None' for key in ['oppositeLineId', 'devId', 'busbarId']):
                message = "输入的{}没有匹配到对应的ID".format(busbar_info)
                send_data = {"type": "chat", "data": message}
                socketio.emit('message', to_json(send_data), room=conversation_id)
                logger.info("create_plan_nn_v2_api fail conv_id:{} raw_query:{} input:{}".format(conversation_id,
                                                                                                       raw_query, input))
    if not subId:
        message = f"没有找到{subName}对应的厂站ID，无法进行方案生成"
        result = {
            'conclusionText': message,
            'conclusionTwoText': message,
        }

        send_data = {"type": "chat", "data": message}
        socketio.emit('message', to_json(send_data), room=conversation_id)

        logger.info("create_plan_nn_v2_api fail conv_id:{} raw_query:{} input:{} result:{}".format(conversation_id, raw_query, input, result))

        return make_api_response(result)

    logger.info("optimize_plan_nn_v2_api debug conv_id:{} raw_query:{} input:{}".format(conversation_id, raw_query, input))

    send_data = {"type": "chat", "data": f"正在进行{subName}全停转供方案优化"}
    socketio.emit('message', to_json(send_data), room=conversation_id)

    data = PlanOptimizeService.optimize_plan_v2(subName=subName, subId=subId,
                                                isYaoKong=isYaoKong, userNumberWeight=userNumberWeight,
                                                lineLoadRateThreshold=lineLoadRateThreshold, isBusBarRecover=isBusBarRecover,
                                                conclusionText=conclusionText, score=score, conclusionTwoText=conclusionTwoText,
                                                turn=turn, faultTime=fault_time, socketio=socketio, conversationId=conversation_id,
                                                busbarNotRepeatLineList=busbarNotRepeatLineList, busbarRepeatLineList=busbarRepeatLineList)

    plan = data['plan']
    text = data['text']
    p = data['params']

    line_name_list = []

    if 'data' not in plan or plan['data'] is None:
        message = '未找到更优化方案'
        result = {
            'conclusionText': message,
            'conclusionTwoText': message,
            'processText': text
        }

        send_data = {"type": "chat", "data": message}
        socketio.emit('message', to_json(send_data), room=conversation_id)

        logger.info("optimize_plan_nn_v2_api fail conv_id:{} raw_query:{} input:{} result:{}".format(conversation_id, raw_query, input, result))

        return make_api_response(result)

    else:
        send_data = {"type": "chat", "data": f"已生成{subName}全停转供优化方案"}
        socketio.emit('message', to_json(send_data), room=conversation_id)

        # 保存最终方案数据，供第三幕使用
        key = "plan_nn_" + conversation_id
        set_cache(key, json.dumps(plan, ensure_ascii=False))

        # 投送给东方电子
        post_plan_info(plan['data'], 'nn')

        # 发送结构化数据
        plan_info = get_plan_nn_info(plan['data'])
        send_data = {
            "type": "plan",
            "data": {
                "plan_type": "n_n",
                "plan_order": "final",
                "plan_info": plan_info,
                "images": {
                    "url1": "http://statics-nrxt.dcloud.sh.dc.sgcc.com.cn:1082/GAS/WebPage/business/gas/bigModelChain/subBusConn.html?sscode=%s&type=N-N&sno=1" % subId,
                    "url2": "http://statics-nrxt.dcloud.sh.dc.sgcc.com.cn:1082/GAS/WebPage/business/gas/bigModelChain/subBusConn.html?sscode=%s&type=N-N&sno=2" % subId,
                    "url3": "http://statics-nrxt.dcloud.sh.dc.sgcc.com.cn:1082/GAS/WebPage/business/gas/bigModelChain/subBusConn.html?sscode=%s&type=N-N&sno=3" % subId,
                },
                "station_info": {
                    "id": subId,
                    "name": subName
                }
            }
        }

        send_data = json.dumps(send_data, ensure_ascii=False)
        socketio.emit('message', send_data, room=conversation_id)

        line_name_list = PlanService.get_plan_nn_opposite_line_name_list(plan=plan, table_name='recoverAndUnableRecoverTable1')

    result = {
        'conclusionText': plan['data']['recoverAndUnableRecoverTable1']['conclusionText'],
        'conclusionTwoText': plan['data']['recoverAndUnableRecoverTable1']['conclusionTwoText'],
        'score': str(plan['data']['recoverAndUnableRecoverTable1']['schemeScore']),
        'subName': subName,
        'isYaoKong': str(p['isYaoKong']),
        'userNumberWeight': str(p['userNumberWeight']),
        'lineLoadRateThreshold': str(p['lineLoadRateThreshold2']),
        'isBusBarRecover': str(p['isBusBarRecover']),
        'oppositeLines': line_name_list,
        'processText': text
    }

    logger.info("optimize_plan_nn_v2_api success conv_id:{} raw_query:{} input:{} result:{}".format(conversation_id, raw_query, input, result))

    return make_api_response(result) #
