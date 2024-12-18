from common import set_cache, get_cache, get_path, get_conversation_id, logger, make_api_response
from flask import make_response
from third.zheda.parser import get_plan_nn_info, get_plan_n1_info, get_plan_single_info
from third.zheda.api import get_map_id, create_plan_n1
from third.nanrui.parser import get_overload_station, get_overload_reason_station
import json, datetime


def create_plan_single_api(request, socketio, app):
    conversation_id = get_conversation_id(request)
    raw_query = request.form.get('raw_query', '')

    logger.info("create_plan_single_api conversation_id:%s raw_query:%s", conversation_id, raw_query)

    # 获取故障信息
    key = "fault_" + conversation_id
    fault = get_cache(key)
    fault = json.loads(fault)

    # 生成转供方案
    st_info = get_overload_station(fault)
    st_reason_info = get_overload_reason_station(fault, st_info)

    send_data = json.dumps({"type": "chat", "data": "正在生成%s单电源转供方案..." % st_info['st_name']}, ensure_ascii=False)
    socketio.emit('message', send_data, room=conversation_id)

    plan = create_plan(fault, st_reason_info)

    plan['data']['subName'] = st_info['st_name']

    # 保存最终方案数据，供第三幕使用
    key = "plan_single_" + conversation_id
    set_cache(key, json.dumps(plan, ensure_ascii=False))

    sub_id = plan['data']['dispatchAccidentPreplanMathFilterVm']['subId']
    dev_id = plan['data']['dispatchAccidentPreplanMathFilterVm']['maintDevice'][0]['devIdList'][0]

    # 发送结构化数据
    plan_info = get_plan_single_info(plan['data'])
    send_data = {
        "type": "plan",
        "data": {
            "plan_type": "single",
            "plan_order": "first",
            "plan_info": plan_info,
            "images": {
                "url1": "http://statics-nrxt.dcloud.sh.dc.sgcc.com.cn:1082/GAS/WebPage/business/gas/bigModelChain/subBusConn.html?sscode=%s&type=N-1&subtype=2&sno=1&transcode=%s" % (sub_id, dev_id),
                "url2": "http://statics-nrxt.dcloud.sh.dc.sgcc.com.cn:1082/GAS/WebPage/business/gas/bigModelChain/subBusConn.html?sscode=%s&type=N-1&subtype=2&sno=2&transcode=%s" % (sub_id, dev_id) if not plan['data']['plan2'] else "",
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

    data = "针对%s单电源，已生成处置方案" % (st_info['st_name'])
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