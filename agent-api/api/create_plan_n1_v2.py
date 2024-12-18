from common import check_weight_number, set_cache, get_cache, get_file, get_conversation_id, logger, to_json, make_api_response, del_kv_info
from flask import make_response
from service.plan import PlanService
from third.dfe.api import post_plan_info
from third.zheda.parser import get_plan_n1_info, get_plan_single_info
import json

# 检查主变重叠
def _check_wind(plan_n1, socketio, conversation_id):
    str = ''
    try:
        key = "plan_nn_" + conversation_id
        plan_nn = get_cache(key, return_json=True)

        map_nn = {}
        if plan_nn is not None:
            map_nn = PlanService.get_plan_nn_opposite_wind_max_load_map(plan_nn, 'recoverAndUnableRecoverTable1')

        map_n1 = PlanService.get_plan_n1_opposite_wind_max_load_map(plan_n1)

        logger.info(f"_check_wind map_nn[{map_nn}] map_n1[{map_n1}]")

        # 重叠列表
        cd_list = []

        if map_nn and map_n1:
            str = f"重载方案转供路径：{','.join(map_n1.keys())}，全停方案转供路径：{','.join(map_nn.keys())}，经校验"
            for k, v in map_n1.items():
                # k = '创立站2号主变' # mock时打开使用
                if k in map_nn:
                    map_nn[k]['max_i'] += float(v['reduce_i'])
                    load = float(map_nn[k]['max_i']) / float(map_nn[k]['total_i']) * 100
                    cd_list.append(f"{k}存在重叠，增加{v['reduce_i']}A， 负载率：%.2f%%%s" % (load, '(重载)' if load >= 90 else ''))

            if cd_list:
                str += '：\n'
                str += '\n'.join(cd_list)
            else:
                str += '不存在重叠。'
        else:
            str = '重载方案的转供路径，经校验不存在与其他方案重叠'
    except Exception as e:
       logger.info(f"_check_wind error[{e}]")
       str = '重载方案的转供路径，经校验不存在与其他方案重叠'

    send_data = {"type": "chat", "data": str}
    socketio.emit('message', to_json(send_data), room=conversation_id)

def create_plan_n1_v2_api(request, socketio, app):
    conversation_id = get_conversation_id(request)
    raw_query = request.form.get('raw_query', '')
    type = request.args.get('type', 'n_1')  # 取值single=单电源，n_1=N-1

    subName = request.form.get('subName', '')
    subNameOri = subName
    subName = del_kv_info(subName)
    subId = PlanService.get_station_id(subName)

    devName = request.form.get('devName', '')
    devNameOri = devName
    devName = del_kv_info(devName)
    devId = PlanService.get_dev_id(devName, subName)

    disableDev = request.form.get('disableDev', '')

    isYaoKong = request.form.get('isYaoKong', '').lower() == 'true'
    userNumberWeight = int(request.form.get('userNumberWeight', '100'))
    userNumberWeight = check_weight_number(userNumberWeight)
    lineLoadRateThreshold = int(request.form.get('lineLoadRateThreshold', '80'))
    lineLoadRateThreshold = check_weight_number(lineLoadRateThreshold)
    isBusBarRecover = request.form.get('isBusBarRecover', '').lower() == 'true'

    input = {
        "type": type,
        "subName": subName,
        "subNameOri": subNameOri,
        "subId": subId,
        "devName": devName,
        "devNameOri": devNameOri,
        "devId": devId,
        "isYaoKong": isYaoKong,
        "userNumberWeight": userNumberWeight,
        "lineLoadRateThreshold": lineLoadRateThreshold,
        "isBusBarRecover": isBusBarRecover,
        "disableDev": disableDev
    }

    message = ''
    if not subId:
        message = f"没有找到{subName}对应的ID，无法进行方案生成"
    elif not devId:
        message = f"没有找到{devName}对应的ID，无法进行方案生成"

    if message:
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

    type_name = '单电源' if type == 'single' else '重载'
    send_data = {"type": "chat", "data": f"正在生成{subName}{type_name}转供方案..."}
    socketio.emit('message', to_json(send_data), room=conversation_id)

    plan = PlanService.create_plan_n1(subId=subId, devId=devId, devName=devName, isYaoKong=isYaoKong, userNumberWeight=userNumberWeight, lineLoadRateThreshold=lineLoadRateThreshold, isBusBarRecover=isBusBarRecover, faultTime=fault_time)
    logger.info("create_plan_n1_v2_api debug conv_id:{} raw_query:{} input:{}".format(conversation_id, raw_query, input))

    if 'data' not in plan or plan['data'] is None:
        message = '方案生成失败，请检查相关参数'
        result = {
            'conclusionText': message,
            'conclusionTwoText': message,
        }

        send_data = {"type": "chat", "data": message}
        socketio.emit('message', to_json(send_data), room=conversation_id)
        logger.info("create_plan_n1_v2_api fail conv_id:{} raw_query:{} input:{} result:{}".format(conversation_id, raw_query, input, result))

        return make_api_response(result)
    else:
        plan['data']['subName'] = subName
        line_name_list = PlanService.get_plan_n1_opposite_line_name_list(plan=plan, type=type)

        send_data = {"type": "chat", "data": f"已生成{subName}{type_name}转供方案..."}
        socketio.emit('message', to_json(send_data), room=conversation_id)

        if type == 'single':  # 单电源
            # 保存最终方案数据，供第三幕使用
            key = "plan_single_" + conversation_id
            set_cache(key, json.dumps(plan, ensure_ascii=False))

            # 发送结构化数据
            plan_info = get_plan_single_info(plan['data'])
            send_data = {
                "type": "plan",
                "data": {
                    "plan_type": "single",
                    "plan_order": "first",
                    "plan_info": plan_info,
                    "images": {
                        "url1": "http://statics-nrxt.dcloud.sh.dc.sgcc.com.cn:1082/GAS/WebPage/business/gas/bigModelChain/subBusConn.html?sscode=%s&type=N-1&subtype=2&sno=1&transcode=%s" % (
                        subId, devId),
                        "url2": "http://statics-nrxt.dcloud.sh.dc.sgcc.com.cn:1082/GAS/WebPage/business/gas/bigModelChain/subBusConn.html?sscode=%s&type=N-1&subtype=2&sno=2&transcode=%s" % (
                        subId, devId) if not plan['data']['plan2'] else "",
                    },
                    "station_info": {
                        "id": subId,
                        "name": subName
                    },
                    "dev_info": {
                        "id": devId,
                        "name": devName
                    }
                }
            }

            socketio.emit('message', to_json(send_data), room=conversation_id)
        else:  # N-1
            # 保存最终方案数据，供第三幕使用
            key = "plan_n1_" + conversation_id
            if len(plan['data']['plan1']['transferTableGroupList'][0]['transferTableList']) != 0:
                set_cache(key, json.dumps(plan, ensure_ascii=False))


            _check_wind(plan_n1=plan, socketio=socketio, conversation_id=conversation_id)

            # 投送给东方电子
            post_plan_info(plan['data'], 'n1')

            # 发送结构化数据
            plan_info = get_plan_n1_info(plan['data'])
            send_data = {
                "type": "plan",
                "data": {
                    "plan_type": "n_1",
                    "plan_order": "first",
                    "plan_info": plan_info,
                    "images": {
                        "url1": "http://statics-nrxt.dcloud.sh.dc.sgcc.com.cn:1082/GAS/WebPage/business/gas/bigModelChain/subBusConn.html?sscode=%s&type=N-1&subtype=1&sno=1&transcode=%s" % (
                            subId, devId),
                        "url2": "http://statics-nrxt.dcloud.sh.dc.sgcc.com.cn:1082/GAS/WebPage/business/gas/bigModelChain/subBusConn.html?sscode=%s&type=N-1&subtype=1&sno=2&transcode=%s" % (
                            subId, devId) if not plan['data']['plan2'] else "",
                    },
                    "station_info": {
                        "id": subId,
                        "name": subName
                    },
                    "dev_info": {
                        "id": devId,
                        "name": devName
                    }
                }
            }

            send_data = json.dumps(send_data, ensure_ascii=False)
            socketio.emit('message', send_data, room=conversation_id)


        result = {
            'type': type,
            'conclusionText': plan['data']['plan1']['transferTableGroupList'][0]['conclusionText'],
            'conclusionTwoText': '',
            'score': str(plan['data']['plan1']['schemeScore']),
            'subName': subName,
            'devName': devName,
            'isYaoKong': str(isYaoKong),
            'userNumberWeight': str(userNumberWeight),
            'lineLoadRateThreshold': str(lineLoadRateThreshold),
            'isBusBarRecover': str(isBusBarRecover),
            'oppositeLines': line_name_list
        }

        logger.info("create_plan_n1_v2_api success conv_id:{} raw_query:{} input:{} result:{}".format(conversation_id, raw_query, input, result))
        return make_api_response(result)
