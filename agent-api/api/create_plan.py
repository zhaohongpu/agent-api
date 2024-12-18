from common import set_cache, get_cache, get_file, get_conversation_id, logger, make_api_response
from third.zheda.parser import get_plan_nn_info
from third.zheda.api import get_map_id, create_plan_nn
from third.dfe.api import post_plan_info
from third.baidu.api import function_call
from service.plan import PlanService
import json
from service.fault import FaultService

def create_plan_api(request, socketio, app):
    conversation_id = get_conversation_id(request)
    raw_query = request.form.get('raw_query', '')

    logger.info("create_plan_api conversation_id:%s raw_query:%s", conversation_id, raw_query)

    # 获取故障信息
    key = "fault_" + conversation_id
    fault = get_cache(key)
    fault = json.loads(fault)

    # 生成转供方案
    st_info = FaultService.get_stop_all_station(fault)

    send_data = json.dumps({"type": "chat", "data": "正在生成%s全停转供方案..." % st_info['st_name']}, ensure_ascii=False)
    socketio.emit('message', send_data, room=conversation_id)

    plan = create_plan(fault, st_info)

    send_data = json.dumps({"type": "chat", "data": "已生成%s全停转供方案，正在进行方案优化" % st_info['st_name']},ensure_ascii=False)
    socketio.emit('message', send_data, room=conversation_id)

    # try:
    #     plan_optimize_service = PlanOptimizeServiceOld(plan, socketio)
    #     plan = plan_optimize_service.optimize_plan()
    #     send_data = json.dumps({"type": "chat", "data": "针对%s全停转供方案，已生成优化方案" % st_info['st_name']}, ensure_ascii=False)
    #     socketio.emit('message', send_data, room=conversation_id)
    # except Exception as e:
    #     logger.error(e)


    # 保存最终方案数据，供第三幕使用
    key = "plan_nn_" + conversation_id
    set_cache(key, json.dumps(plan, ensure_ascii=False))

    # 投送给东方电子
    post_plan_info(plan['data'], 'nn')
    sub_id = plan['data']['dispatchAccidentPreplanMathFilterVm']['subId']

    # 发送结构化数据
    plan_info = get_plan_nn_info(plan['data'])
    send_data = {
        "type": "plan",
        "data": {
            "plan_type": "n_n",
            "plan_order": "first",
            "plan_info": plan_info,
            "images": {
                "url1": "http://statics-nrxt.dcloud.sh.dc.sgcc.com.cn:1082/GAS/WebPage/business/gas/bigModelChain/subBusConn.html?sscode=%s&type=N-N&sno=1" % sub_id,
                "url2": "http://statics-nrxt.dcloud.sh.dc.sgcc.com.cn:1082/GAS/WebPage/business/gas/bigModelChain/subBusConn.html?sscode=%s&type=N-N&sno=2" % sub_id,
                "url3": "http://statics-nrxt.dcloud.sh.dc.sgcc.com.cn:1082/GAS/WebPage/business/gas/bigModelChain/subBusConn.html?sscode=%s&type=N-N&sno=3" % sub_id,
            },
            "station_info": {
                "id": get_map_id(st_info['st_id']),
                "name": st_info['st_name']
            }
        }
    }

    send_data = json.dumps(send_data, ensure_ascii=False)
    socketio.emit('message', send_data, room=conversation_id)

    data = "针对%s全站失电，已生成3组处置方案" % st_info['st_name']
    send_data = json.dumps({"type": "chat", "data": data}, ensure_ascii=False)
    socketio.emit('message', send_data, room=conversation_id)

    result = {
        "code": 0,
        "message": "OK",
        "data": data
    }

    return make_api_response(result)


def create_plan(fault, st_info):
    cloud_sub_id = st_info['st_id']
    sub_id = get_map_id(cloud_sub_id)

    response = PlanService.create_plan_nn(subId=sub_id)
    return response