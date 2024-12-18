from common import set_cache, get_cache, get_path, get_conversation_id, logger, make_api_response
from third.zheda.parser import get_plan_nn_info, get_plan_n1_info
from third.zheda.api import get_map_id, create_plan_nn, create_plan_n1
from third.nanrui.parser import get_overload_station, get_overload_reason_station
from third.dfe.api import post_plan_info
import json
import datetime


def create_plan_n1_api(request, socketio, app):
    conversation_id = get_conversation_id(request)
    raw_query = request.form.get('raw_query', '')

    logger.info("create_plan_n1_api conversation_id:%s raw_query:%s", conversation_id, raw_query)

    # 获取故障信息
    key = "fault_" + conversation_id
    fault = get_cache(key)
    fault = json.loads(fault)

    # 生成转供方案
    st_info = get_overload_station(fault)
    st_reason_info = get_overload_reason_station(fault, st_info)

    logger.info("create_plan_n1_api st_info:%s st_reason_info:%s" % (st_info, st_reason_info))

    send_data = json.dumps({"type": "chat", "data": "正在生成%s%s重载转供方案..." % (st_info['st_name'], st_info['warn_dev_name'])}, ensure_ascii=False)
    socketio.emit('message', send_data, room=conversation_id)

    plan = create_plan(fault, st_reason_info)

    plan['data']['subName'] = st_info['st_name']

    # 保存最终方案数据，供第三幕使用
    key = "plan_n1_" + conversation_id
    set_cache(key, json.dumps(plan, ensure_ascii=False))

    # 投送给东方电子
    post_plan_info(plan['data'], 'n1')
    sub_id = plan['data']['dispatchAccidentPreplanMathFilterVm']['subId']
    dev_id = plan['data']['dispatchAccidentPreplanMathFilterVm']['maintDevice'][0]['devIdList'][0]

    # 发送结构化数据
    plan_info = get_plan_n1_info(plan['data'])
    send_data = {
        "type": "plan",
        "data": {
            "plan_type": "n_1",
            "plan_order": "first",
            "plan_info": plan_info,
            "images": {
                "url1": "http://statics-nrxt.dcloud.sh.dc.sgcc.com.cn:1082/GAS/WebPage/business/gas/bigModelChain/subBusConn.html?sscode=%s&type=N-1&subtype=1&sno=1&transcode=%s" % (sub_id, dev_id),
                "url2": "http://statics-nrxt.dcloud.sh.dc.sgcc.com.cn:1082/GAS/WebPage/business/gas/bigModelChain/subBusConn.html?sscode=%s&type=N-1&subtype=1&sno=2&transcode=%s" % (sub_id, dev_id) if not plan['data']['plan2'] else "",
            },
            "station_info": {
                "id": get_map_id(st_info['warn_st']),
                "name": st_info['st_name']
            },
            "dev_info": {
                "id": get_map_id(st_reason_info['off_dev']),
                "name": st_reason_info['dev_name']
            }
        }
    }

    send_data = json.dumps(send_data, ensure_ascii=False)
    socketio.emit('message', send_data, room=conversation_id)

    desc = """针对横沔站全站失电，大模型优化“影响负荷和影响用户数2个指标扣分较多，调整【是否允许非遥控操作】为True，调整【线路负载率上限（分架空/电缆、分电压等级）】为115，调整【是否允许操作母联开关】为True。”，已生成3组处置方案。根据历史故障处置信息，推荐选择方案四，请确认选择哪组方案。
    方案四：无失电负荷，无设备重过载，操作量50单位时长。
    方案五：无失电负荷，1台35kV主变负载率达到90%，操作量25时长。
    方案六：1MW失电负荷未复电，无设备重过载，操作量20单位时长。
    针对医高站主变重载，已生成3组处置方案。根据历史故障处置信息，推荐选择方案二，请确认选择哪组方案。
    方案一：无失电负荷，无设备重过载，操作量50单位时长。
    方案二：无失电负荷，1条10kV线路负载率达到80%，主变无重过载，操作量25时长。
    方案三：无失电负荷，1台35kV主变负载率达到81%（且负载率依然有上涨趋势），操作量20单位时长。
    横沔站全站失电以及医高站主变重载的备选转供方案，存在回路上级电源通道重叠，经校验后，涉及越限。根据故障优先级、严重程度，优先调整主变重过载的参数。

    针对主变越限，已重新生成3组处置方案。根据历史故障处置信息，推荐选择方案二，请确认选择哪组方案。
    方案一：无失电负荷，无设备重过载，操作量55单位时长。
    方案二：无失电负荷，1条10kV线路负载率达到81%，主变无重过载，操作量30时长。
    方案三：无失电负荷，1台35kV主变负载率达到82%（且负载率依然有上涨趋势），操作量20单位时长。
    建议执行全站停电方案一，主变过载方案二。"""

    data = "针对%s%s重载，已生成处置方案" % (st_info['st_name'], st_info['warn_dev_name'])
    send_data = json.dumps({"type": "chat", "data": data}, ensure_ascii=False)
    socketio.emit('message', send_data, room=conversation_id)

    result = {
        "code": 0,
        "message": "OK",
        "data": data
    }

    return make_api_response(result)


def create_plan(fault, dev):
    timestamp = fault['fault_list'][0]['fault_sec']
    dt_object = datetime.datetime.fromtimestamp(timestamp)
    formatted_date = dt_object.strftime("%Y-%m-%d")
    sub_id = get_map_id(dev['first_st'])
    dev_id = get_map_id(dev['off_dev'])

    vm = {
      "type": "N-1",
      "subId": sub_id,
      "maintDevice": [
        {
          "type": "TRAN",
          "devIdList": [
            dev_id
          ],
          "text": dev['dev_name']
        }
      ],
      "busbarReceiveLineList": [  # 可以不传

      ],
      "faultLineList": [],
      "notPjLineList": [],
      "beginDate": "2024-08-02",  # 动态取时间不对
      "endDate": "2024-08-02",
      "beginTime": "00:00:00",
      "endTime": "23:59:59",
      "dtFileTime": None,
      "joinCutType": None,
      "lineLoadRateThreshold": 100,
      "loadRateSetupDTOList": [],
      "isHeavyLoad": False,
      "isYaoKong": True,
      "isAreaDifferent": True,
      "isImportantUserSingle": True,
      "isImportantUserSuperSingle": True,
      "busbarRepeatLineList": [],
      "busbarNotRepeatLineList": [],
      "isBusBarRecover": True,
      "mathematicalObjective": {
        "loadObjective": {
          "unit": 10,
          "weight": 100
        },
        "userLoadObjective": {
          "unit": 10,
          "weight": 500
        },
        "areaNumObjective": {
          "unit": 1,
          "weight": 20
        },
        "notYaoKongNumObjective": {
          "unit": 1,
          "weight": 10
        },
        "yaoKongNumObjective": {
          "unit": 1,
          "weight": 1
        },
        "userNumberObjective": {
          "unit": 10,
          "weight": 0
        },
        "importantUserNumberObjective": {
          "unit": 1,
          "weight": 0
        }
      }
    }

    response = create_plan_n1(vm)
    return response
