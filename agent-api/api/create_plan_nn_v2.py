from ban_or_enforced import is_ban_or_enforced
from common import check_weight_number, set_cache, get_cache, get_conversation_id, logger, make_api_response, \
    to_json
from flask import make_response
from service.plan import PlanService
from third.dfe.api import post_plan_info
from third.zheda.parser import get_plan_nn_info
from common import del_kv_info
import json
import time

def create_plan_nn_v2_api(request, socketio, app):
    conversation_id = get_conversation_id(request)
    raw_query = request.form.get('raw_query', '')

    subName = request.form.get('subName', '')
    subNameOri = subName
    subName = del_kv_info(subName)
    busbarNotRepeatLineList, busbarRepeatLineList = is_ban_or_enforced(raw_query, subName)

    subId = PlanService.get_station_id(subName)
    disableDev = request.form.get('disableDev', '')

    isYaoKong = request.form.get('isYaoKong', '').lower() == 'true'
    userNumberWeight = int(request.form.get('userNumberWeight', '100'))
    userNumberWeight = check_weight_number(userNumberWeight)
    lineLoadRateThreshold = int(request.form.get('lineLoadRateThreshold', '80'))
    lineLoadRateThreshold = check_weight_number(lineLoadRateThreshold)
    isBusBarRecover = request.form.get('isBusBarRecover', '').lower() == 'true'

    input = {
        "subName": subName,
        "subNameOri": subNameOri,
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

    # 故障信息
    key = "fault_" + conversation_id
    fault = get_cache(key, return_json=True)
    fault_time = fault['fault_list'][0]['fault_sec'] if fault is not None else None

    send_data = {"type": "chat", "data": f"正在生成{subName}全停转供方案中..."}
    socketio.emit('message', to_json(send_data), room=conversation_id)

    logger.info("create_plan_nn_v2_api debug conv_id:{} raw_query:{} input:{}".format(conversation_id, raw_query, input))

    # 加缓存提升性能的逻辑
    cache_key = f"{conversation_id}_{subId}_{isYaoKong}_{userNumberWeight}_{lineLoadRateThreshold}_{isBusBarRecover}_{fault_time}".lower()
    plan = get_cache(cache_key, return_json=True)
    if plan is None or 'data' not in plan or plan['data'] is None:
        startTime = int(time.time())
        plan = PlanService.create_plan_nn(subId, isYaoKong=isYaoKong, userNumberWeight=userNumberWeight,
                                          lineLoadRateThreshold=lineLoadRateThreshold, isBusBarRecover=isBusBarRecover,
                                          faultTime=fault_time, busbarNotRepeatLineList=busbarNotRepeatLineList,
                                          busbarRepeatLineList=busbarRepeatLineList)
        cost = int(time.time()) - startTime
        logger.info(f"create_plan_nn_v2_api cost[{cost}s] cache_key[{cache_key}] get_plan_from_cache fail, get_from_zheda")
        # set_cache(cache_key, plan)
    else:
        logger.info(f"create_plan_nn_v2_api cache_key[{cache_key}] get_plan_from_cache success")

    if plan is None or 'data' not in plan or plan['data'] is None:
        message = '方案生成失败，请检查相关参数'
        result = {
            'conclusionText': message,
            'conclusionTwoText': message,
        }

        send_data = {"type": "chat", "data": message}
        socketio.emit('message', to_json(send_data), room=conversation_id)

        logger.info("create_plan_nn_v2_api fail conv_id:{} raw_query:{} input:{} result:{}".format(conversation_id, raw_query, input, result))

        return make_api_response(result)
    else:
        line_name_list = PlanService.get_plan_nn_opposite_line_name_list(plan=plan, table_name='recoverAndUnableRecoverTable1')
        send_data = {"type": "chat", "data": f"已生成{subName}全停转供方案"}
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
                "plan_order": "first",
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

        result = {
            'type': 'n_n',
            'conclusionText': plan['data']['recoverAndUnableRecoverTable1']['conclusionText'],
            'conclusionTwoText': plan['data']['recoverAndUnableRecoverTable1']['conclusionTwoText'],
            'score': str(plan['data']['recoverAndUnableRecoverTable1']['schemeScore']),
            'subName': subName,
            'isYaoKong': str(isYaoKong),
            'userNumberWeight': str(userNumberWeight),
            'lineLoadRateThreshold': str(lineLoadRateThreshold),
            'isBusBarRecover': str(isBusBarRecover),
            'oppositeLines': line_name_list
        }

        logger.info("create_plan_nn_v2_api success conv_id:{} raw_query:{} input:{} result:{}".format(conversation_id, raw_query, input, result))
        return make_api_response(result)