import os

from common import get_file, get_path, set_cache, logger, is_mock_third_api, to_json, del_kv_info
from third.baidu.api import function_call, llm_call
from third.zheda.api import create_plan_nn, create_plan_n1
import json
import datetime
import time

id_map = get_file('/demo/id_map.json', return_json=True)
oppositeLineId_map = get_file('/demo/loadMapping.json', return_json=True)
busbarId_map = get_file('/demo/busbar_map.json', return_json=True)

class PlanService:
    @staticmethod
    def create_plan_nn(subId, isYaoKong=True, userNumberWeight=0, lineLoadRateThreshold=80, isBusBarRecover=True, busbarNotRepeatLineList=[], busbarRepeatLineList=[], faultTime=None):
        beginDate = "2024-08-02"
        beginTime = "00:00:00"
        endDate = "2024-08-02"
        endTime = "23:59:59"
        vm = {
            "type": "N-N",
            "subId": subId,
            "maintDevice": [

            ],
            "busbarReceiveLineList": [

            ],
            "faultLineList": [

            ],
            "notPjLineList": [

            ],
            "beginDate": beginDate,  # 动态传时间不对
            "endDate": endDate,
            "beginTime": beginTime,
            "endTime": endTime,
            "dtFileTime": None,
            "joinCutType": None,
            "lineLoadRateThreshold": lineLoadRateThreshold,
            "loadRateSetupDTOList": [
            ],
            "isYaoKong": isYaoKong,
            "busbarRepeatLineList": busbarRepeatLineList,
            "busbarNotRepeatLineList": busbarNotRepeatLineList,
            "isBusBarRecover": isBusBarRecover,
            "isHeavyLoad": True,
            "isAreaDifferent": True,
            "isImportantUserSingle": True,
            "isImportantUserSuperSingle": True,
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
                    "weight": userNumberWeight
                },
                "importantUserNumberObjective": {
                    "unit": 1,
                    "weight": 0
                }
            }
        }

        response = create_plan_nn(vm)
        return response

    @staticmethod
    def create_plan_n1(subId="", devId="", devName="", isYaoKong=True, userNumberWeight=0, lineLoadRateThreshold=80, isBusBarRecover=True, busbarNotRepeatLineList=[], faultTime=None):
        # 默认时间日期，动态改时间有时不能出数据，待排查
        beginDate = "2024-08-02"
        beginTime = "00:00:00"
        endDate = "2024-08-02"
        endTime = "23:59:59"

        # if faultTime is not None:
        #     faultTime += 8 * 3600 # 修正为北京时间
        #     start_timestamp = datetime.datetime.utcfromtimestamp(faultTime - 60 * 60)
        #     end_timestamp = datetime.datetime.utcfromtimestamp(faultTime)
        #
        #     beginDate = start_timestamp.strftime('%Y-%m-%d')
        #     beginTime = start_timestamp.strftime('%H:%M:%S')
        #
        #     endDate = end_timestamp.strftime('%Y-%m-%d')
        #     endTime = end_timestamp.strftime('%H:%M:%S')

        vm = {
            "type": "N-1",
            "subId": subId,
            "maintDevice": [
                {
                    "type": "TRAN",
                    "devIdList": [
                        devId
                    ],
                    "text": devName
                }
            ],
            "busbarReceiveLineList": [

            ],
            "faultLineList": [

            ],
            "notPjLineList": [

            ],
            "beginDate": beginDate,  # 动态传时间不对
            "endDate": endDate,
            "beginTime": beginTime,
            "endTime": endTime,
            "dtFileTime": None,
            "joinCutType": None,
            "lineLoadRateThreshold": lineLoadRateThreshold,
            "loadRateSetupDTOList": [

            ],
            "isYaoKong": isYaoKong,
            "busbarRepeatLineList": [

            ],
            "busbarNotRepeatLineList": busbarNotRepeatLineList,
            "isBusBarRecover": isBusBarRecover,
            "isHeavyLoad": True,
            "isAreaDifferent": True,
            "isImportantUserSingle": True,
            "isImportantUserSuperSingle": True,
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
                    "weight": userNumberWeight
                },
                "importantUserNumberObjective": {
                    "unit": 1,
                    "weight": 0
                }
            }
        }

        response = create_plan_n1(vm)
        return response

    @staticmethod
    def get_station_id(station_name):
        station_name = del_kv_info(station_name)
        return id_map.get(station_name, '')

    @staticmethod
    def get_dev_id(dev_name, station_name = ''):
        station_name = del_kv_info(station_name)
        dev_name = del_kv_info(dev_name)
        if '.' in dev_name:
            dev_name = dev_name.split('.')[1]

        id = id_map.get(station_name+dev_name, '')
        if not id:
            id = id_map.get(dev_name)

        return id

    @staticmethod
    def get_plan_nn_opposite_line_name_list(plan=None, table_name=""):
        list = []
        try:
            for r in plan['data'][table_name]['recoverTable']['rowList']:
                list.append(r['oppositeLine'])
        except Exception as e:
            logger.info(f"get_plan_nn_opposite_line_name_list error[{e}]")

        return list

    @staticmethod
    def get_plan_n1_opposite_line_name_list(plan=None, type=""):
        list = []

        try:
            if type == 'single':
                for r in plan['data']['plan1']['lineAndAndOppositeLines']:
                    list.append(r['oppositeLineDeviceDto']['devNameRemoveSubName'])
            else:
                for r in plan['data']['plan1']['transferTableGroupList'][0]['transferTableList'][0]['rowList']:
                    list.append(r['oppositeLine'])
        except Exception as e:
            logger.info(f"get_plan_n1_opposite_line_name_list type[{type}] error[{e}]")

        return list

    @staticmethod
    def _parse_load_info(str):
        str = str.replace('A', '')
        str = str.replace('%', '')
        arr = str.split('\n')
        name = arr[1]
        max_i = float(arr[0].split('/')[0])
        load = float(arr[0].split('/')[1]) / 100
        total_i = max_i / load

        return {
            'name': name,
            'max_i': max_i,
            'total_i': total_i,
            'load': load
        }

    @staticmethod
    def get_plan_nn_opposite_wind_max_load_map(plan=None, table_name=""):
        map = {}
        try:
            for r in plan['data'][table_name]['recoverTable']['rowList']:
                # "oppositeTranMaxLoad": "988A/90%\n金科站2号主变",
                info = PlanService._parse_load_info(r['oppositeTranMaxLoad'])
                map[info['name']] = info
        except Exception as e:
            logger.info(f"get_plan_nn_opposite_wind_max_load_map error[{e}]")

        return map

    @staticmethod
    def get_plan_n1_opposite_wind_max_load_map(plan=None):
        map = {}

        try:
            for r in plan['data']['plan1']['transferTableGroupList'][0]['transferTableList'][0]['rowList']:
                info = PlanService._parse_load_info(r['oppositeTranMaxLoad'])
                info['reduce_i'] = float(r['accumulatedReduceLoad'].replace('A', ''))
                map[info['name']] = info
        except Exception as e:
            logger.info(f"get_plan_n1_opposite_wind_max_load_map error[{e}]")

        return map


class PlanOptimizeService:

    @staticmethod
    def del_station(x):
        if "厂站最高负载率" not in x:
            return x
        x = x.split("站", 1)[1]
        x = x.split("厂站最高负载率", 1)[0] + x.split("；", 1)[1]
        return x

    @staticmethod
    def get_similar_plan(isYaoKong=True, userNumberWeight=0, lineLoadRateThreshold=80, isBusBarRecover=True,
                         conclusionTwoText="", top_num=20):
        query = '参数: **是否允许操作非遥控开关**: {} **复电用户数权重**：{} **线路过载限值**: {} **是否允许母线复电**: {} 方案描述: {}'.format(
            isYaoKong,
            userNumberWeight,
            lineLoadRateThreshold, isBusBarRecover,
            conclusionTwoText)

        if is_mock_third_api():
            return []

        result = function_call('plan_search', query, is_print_log=False)
        result = json.loads(result['answer'])

        return result['list'][:top_num]

    @staticmethod
    def select_best_plan(list, conclusionText, conclusionTwoText, top_num=10, exclude_map={}):
        list2 = []
        for index, v in enumerate(list):
            if f"{index}" in exclude_map:
                continue

            if len(list2) > top_num:
                break

            desc = v['content'].split('value: ')[1]
            line = """==========方案_%d==========\n%s""" % (index, desc)
            list2.append(line)

        if len(list2) == 0:
            return {}

        list = "\n".join(list2)
        this_plan = "{}\n{}".format(conclusionTwoText, conclusionText)

        query = """
        下面是一个需要调整的负荷转供方案，之后我会提供一组相似的负荷转供方案描述以及对应的调节策略，你需要综合判断方案的相似程度以及相同调节策略的数量，选择你的调节策略。
        判断相似程度时，优先选择参数相同的方案。
        ============== 本方案 ================
        %s
        =====================================
        下面是几组相似的转供方案，以及对应的调节策略
        %s

        请你首先判断哪个方案与本方案最相似，再根据相似方案的调节策略决定本方案的调节策略。
        输出中需要包含相似方案编号和参数的调整策略，不要包含任何的思考过程。

        以下是一个输出样例：
        ```json
        {
            "相似方案编号": "方案_2",
            "调整参数": {
                "是否允许操作非遥控开关": True,
                "复电用户数权重": 100,
                "线路过载限值": "增加",
                "是否允许母线复电": True
            }
        }
        ```""" % (this_plan, list)

        if is_mock_third_api():
            return {}

        # result = function_call('plan_select', query)
        response = llm_call(query)
        if 'result' not in response:
            return {}

        json_str = response['result']
        json_str = json_str.replace("```json", "")
        json_str = json_str.replace("```", "")
        json_str = json_str.replace("True", "true")
        json_str = json_str.replace("False", "false")
        json_data = json.loads(json_str)

        result = {
            'data': response,
            'index': int(json_data['相似方案编号'].split('_')[1]),
            'params': {
                'isYaoKong': json_data['调整参数']['是否允许操作非遥控开关'],
                'userNumberWeight': json_data['调整参数']['复电用户数权重'],
                'lineLoadRateThreshold': json_data['调整参数']['线路过载限值'],
                'isBusBarRecover': json_data['调整参数']['是否允许母线复电']
            }
        }

        return result

    @staticmethod
    def parse_value_params(value):
        # value = "调节策略:\n\n**是否允许操作非遥控开关**: False\n**复电用户数权重**：0\n**线路过载限值**: 增加\n**是否允许母线复电**: True\n原方案分数"
        value = value.split('调节策略:')[1]
        value = value.split('原方案分数')[0]
        value = value.replace('\n', '')
        value = value.replace('：', '')
        value = value.replace(':', '')
        value = value.replace(' ', '').strip()
        value = value.split('**')

        p = {}
        p['isYaoKong'] = value[2].lower() == 'true'
        p['userNumberWeight'] = int(value[4])
        p['lineLoadRateThreshold'] = value[6]
        p['isBusBarRecover'] = value[8].lower() == 'true'

        return p

    @staticmethod
    def optimize_plan(old_plan):
        subName = old_plan['data']['subName']
        conclusionText = old_plan['data']['recoverAndUnableRecoverTable1']['conclusionText']
        conclusionText = conclusionText.replace(subName, '').strip()
        conclusionTwoText = PlanOptimizeService.del_station(old_plan['data']['recoverAndUnableRecoverTable1']['conclusionTwoText'])
        vm = old_plan['data']['dispatchAccidentPreplanMathFilterVm']

        old_p = {
            'isYaoKong': vm['isYaoKong'],
            'userNumberWeight': vm['mathematicalObjective']['userNumberObjective']['weight'],
            'lineLoadRateThreshold': int(vm['lineLoadRateThreshold']),
            'isBusBarRecover': vm['isBusBarRecover']
        }

        list = PlanOptimizeService.get_similar_plan(isYaoKong=vm['isYaoKong'], userNumberWeight=vm['mathematicalObjective']['userNumberObjective']['weight'], lineLoadRateThreshold=int(vm['lineLoadRateThreshold']), isBusBarRecover=vm['isBusBarRecover'],
                         conclusionTwoText=conclusionTwoText, top_num=4)

        select_result = PlanOptimizeService.select_best_plan(list, conclusionText=conclusionText, conclusionTwoText=conclusionTwoText)

        p = select_result.get('params', {})
        if is_mock_third_api():
            p['isYaoKong'] = True
            p['userNumberWeight'] = 100
            p['lineLoadRateThreshold'] = 100
            p['isBusBarRecover'] = True

        set_cache('old_plan', old_plan)
        new_plan = PlanService.create_plan_nn(subId=vm['subId'], isYaoKong=p['isYaoKong'], userNumberWeight=p['userNumberWeight'], lineLoadRateThreshold=p['lineLoadRateThreshold'], isBusBarRecover=p['isBusBarRecover'])
        set_cache('new_plan', new_plan)

        logger.info("optimize_plan old_plan p:{} score:{}".format(old_p, old_plan['data']['recoverAndUnableRecoverTable1']['schemeScore']))
        logger.info("optimize_plan new_plan p:{} score:{}".format(p, new_plan['data']['recoverAndUnableRecoverTable1']['schemeScore']))

        return new_plan

    @staticmethod
    def select_best_score_plan(list, exclude_map={}):
        max_score = 0
        max_value = ""
        max_index = 0
        for index, v in enumerate(list):
            if f"{index}" in exclude_map:
                continue

            value = v['content'].split('value: ')[1]
            up_score = float(value.split('分数提升:')[1])
            if up_score > max_score:
                max_score = up_score
                max_value = value
                max_index = index

        if len(max_value) == 0:
            return {}

        return {
            'index': max_index,
            'value': max_value,
            'params': PlanOptimizeService.parse_value_params(max_value)
        }


    @staticmethod
    def remove_repeat_list(list):
        r = {}
        list2 = []
        for index, v in enumerate(list):
            value = v['content'].split('value: ')[1]
            p = PlanOptimizeService.parse_value_params(value)

            key = f"{p['isYaoKong']}_{p['userNumberWeight']}_{p['lineLoadRateThreshold']}_{p['isBusBarRecover']}"

            if key not in r:
                r[key] = 1
                list2.append(v)

        return list2



    @staticmethod
    def optimize_plan_v2(subName, subId, isYaoKong, userNumberWeight, lineLoadRateThreshold, isBusBarRecover,
                         conclusionText, conclusionTwoText, score=0, turn=3, faultTime=None,
                         socketio=None,
                         conversationId=None,
                         busbarNotRepeatLineList=[],
                         busbarRepeatLineList=[]):
        messages = []
        new_plan = {}
        params = {}

        max_score = score

        back_map = {}

        index = 1
        while index <= turn:
            logger.info(f"\n==========第{index}轮进行中========")
            if socketio and conversationId:
                send_data = {"type": "chat", "data": f"第{index}轮优化进行中..."}
                socketio.emit('message', to_json(send_data), room=conversationId)

            conclusionText2 = conclusionText.replace(subName, "").strip()
            conclusionTwoText2 = PlanOptimizeService.del_station(conclusionTwoText)

            exclude_map = {}

            # 检索方案
            old_list = PlanOptimizeService.get_similar_plan(isYaoKong=isYaoKong, userNumberWeight=userNumberWeight,
                                                        lineLoadRateThreshold=lineLoadRateThreshold,
                                                        isBusBarRecover=isBusBarRecover,
                                                        conclusionTwoText=conclusionTwoText2,
                                                        top_num=20)

            list = PlanOptimizeService.remove_repeat_list(old_list)

            logger.info(f"搜索结果参数去重：old_length:{len(old_list)} new_length:{len(list)}")

            trace = {
                'ori_score': score,
                'ori_isYaoKong': isYaoKong,
                'ori_userNumberWeight': userNumberWeight,
                'ori_lineLoadRateThreshold': lineLoadRateThreshold,
                'ori_isBusBarRecover': isBusBarRecover,
                'ori_conclusionText': conclusionText,
                'ori_conclusionTwoText': conclusionTwoText,
            }

            results = []
            # 选分数最大的
            score_result = PlanOptimizeService.select_best_score_plan(list, exclude_map=exclude_map)
            if 'index' in score_result:
                logger.info(f"select_best_score_plan {score_result}")
                exclude_map[f"{score_result['index']}"] = True
                results.append(score_result)

            # 选最相似的
            select_result = PlanOptimizeService.select_best_plan(list, conclusionText=conclusionText2,
                                                                 conclusionTwoText=conclusionTwoText2, top_num=10, exclude_map=exclude_map)
            if 'index' in select_result:
                logger.info(f"select_best_plan_by_llm {select_result}")
                exclude_map[f"{select_result['index']}"] = True
                results.append(select_result)

            # 本批次中分数最高、大模型选优分别执行
            for k, result in enumerate(results):
                p = result['params']
                if p['lineLoadRateThreshold'] == '增加':
                    p['lineLoadRateThreshold2'] = trace['ori_lineLoadRateThreshold'] + 10
                elif p['lineLoadRateThreshold'] == '减少':
                    p['lineLoadRateThreshold2'] = trace['ori_lineLoadRateThreshold'] - 10
                else:
                    p['lineLoadRateThreshold2'] = trace['ori_lineLoadRateThreshold']

                if p['lineLoadRateThreshold2'] >= 100:
                    p['lineLoadRateThreshold2'] = 100

                if p['lineLoadRateThreshold2'] <= 80:
                    p['lineLoadRateThreshold2'] = 80

                trace['opt_isYaoKong'] = p['isYaoKong']
                trace['opt_userNumberWeight'] = p['userNumberWeight']
                trace['opt_lineLoadRateThreshold'] = p['lineLoadRateThreshold2']
                trace['opt_isBusBarRecover'] = p['isBusBarRecover']

                key = f"{p['isYaoKong']}_{p['userNumberWeight']}_{p['lineLoadRateThreshold2']}_{p['isBusBarRecover']}"
                if key in back_map:
                    text = f"""第{index}轮第{k + 1}次优化，本组参数之前已执行，本次跳过：
是否允许操作非遥控开关：{trace['ori_isYaoKong']} --> {trace['opt_isYaoKong']}
复电用户数权重：{trace['ori_userNumberWeight']} --> {trace['opt_userNumberWeight']}
线路负载率限值：{trace['ori_lineLoadRateThreshold']} --> {trace['opt_lineLoadRateThreshold']}
是否允许母联复电：{trace['ori_isBusBarRecover']} --> {trace['opt_isBusBarRecover']}\n"""
                    logger.info(text)
                    messages.append(text)

                    if socketio and conversationId:
                        send_data = {"type": "chat", "data": text}
                        socketio.emit('message', to_json(send_data), room=conversationId)
                    continue
                else:
                    back_map[key] = True

                plan = PlanService.create_plan_nn(subId, isYaoKong=p['isYaoKong'],
                                                  userNumberWeight=p['userNumberWeight'],
                                                  lineLoadRateThreshold=p['lineLoadRateThreshold2'],
                                                  isBusBarRecover=p['isBusBarRecover'], faultTime=faultTime,
                                                  busbarNotRepeatLineList=busbarNotRepeatLineList,
                                                  busbarRepeatLineList=busbarRepeatLineList
                                                  )

                if 'data' not in plan or plan['data'] is None:
                    text = f"""第{index}轮第{k + 1}次优化方案生成失败\n"""
                    logger.info(text)
                    messages.append(text)

                    if socketio and conversationId:
                        send_data = {"type": "chat", "data": text}
                        socketio.emit('message', to_json(send_data), room=conversationId)
                    continue

                trace['opt_score'] = plan['data']['recoverAndUnableRecoverTable1']['schemeScore']
                trace['opt_conclusionText'] = plan['data']['recoverAndUnableRecoverTable1']['conclusionText']
                trace['opt_conclusionTwoText'] = plan['data']['recoverAndUnableRecoverTable1']['conclusionTwoText']

                up_text = "有提升" if trace['opt_score'] > max_score else "无进一步提升"

                text = f"""第{index}轮第{k+1}次优化结果，本轮分数{up_text}
得分对比：{trace['ori_score']} --> {trace['opt_score']}
是否允许操作非遥控开关：{trace['ori_isYaoKong']} --> {trace['opt_isYaoKong']}
复电用户数权重：{trace['ori_userNumberWeight']} --> {trace['opt_userNumberWeight']}
线路负载率限值：{trace['ori_lineLoadRateThreshold']} --> {trace['opt_lineLoadRateThreshold']}
是否允许母联复电：{trace['ori_isBusBarRecover']} --> {trace['opt_isBusBarRecover']}\n"""

                logger.info(text)
                messages.append(text)

                if socketio and conversationId:
                    send_data = {"type": "chat", "data": text}
                    socketio.emit('message', to_json(send_data), room=conversationId)

                if trace['opt_score'] > max_score:
                    # 有分数提升就退出本批次
                    max_score = trace['opt_score']
                    new_plan = plan
                    params = p

                    # 更新检索参数进入下一轮
                    isYaoKong = trace['opt_isYaoKong']
                    userNumberWeight = trace['opt_userNumberWeight']
                    lineLoadRateThreshold = trace['opt_lineLoadRateThreshold']
                    isBusBarRecover = trace['opt_isBusBarRecover']
                    conclusionText = trace['opt_conclusionText']
                    conclusionTwoText = trace['opt_conclusionTwoText']
                    score = trace['opt_score']

            index += 1

        return {
            'plan': new_plan,
            'message': messages,
            'text': '\n'.join(messages),
            'params': params
        }

if __name__ == '__main__':
    plan_nn = get_file('/demo/plan_nn.json', return_json=True)
    plan_n1 = get_file('/demo/plan_n1.json', return_json=True)

    map_nn = PlanService.get_plan_nn_opposite_wind_max_load_map(plan_nn, 'recoverAndUnableRecoverTable1')
    map_n1 = PlanService.get_plan_n1_opposite_wind_max_load_map(plan_n1)

    str = ''
    if map_nn and map_n1:
        str = f"重载方案转供路径：{','.join(map_n1.keys())}，全停方案转供路径：{','.join(map_nn.keys())}，经校验"
        tag = False
        for k, v in map_n1.items():
            if k in map_nn:
                tag = True
                break

        str += '存在重叠。' if tag else '不存在重叠。'
    else:
        str = '重载方案的转供路径，经校验不存在与其他方案重叠'

    print(str)



    subId = "113997367262314626"

    beginDate = "2024-08-02"
    beginTime = "00:00:00"
    endDate = "2024-08-02"
    endTime = "23:59:59"

    isYaoKong = True
    userNumberWeight = 0
    lineLoadRateThreshold = 80
    isBusBarRecover = True
    busbarNotRepeatLineList = [
        {
            "busbarId":"115404742145868059",
            "busbarName":"横沔站10kV二、三段母线",
            "devId":"115967692099290101",
            "devName":"横沔站横22火箭",
            "oppositeLineId":"115967692099289456",
            "oppositeLineName":"创立站创37康新",
        }
    ]

    vm = {
        "type": "N-N",
        "subId": subId,
        "maintDevice": [

        ],
        "busbarReceiveLineList": [

        ],
        "faultLineList": [

        ],
        "notPjLineList": [

        ],
        "beginDate": beginDate,  # 动态传时间不对
        "endDate": endDate,
        "beginTime": beginTime,
        "endTime": endTime,
        "dtFileTime": None,
        "joinCutType": None,
        "lineLoadRateThreshold": lineLoadRateThreshold,
        "loadRateSetupDTOList": [

        ],
        "isYaoKong": isYaoKong,
        "busbarRepeatLineList": [

        ],
        "busbarNotRepeatLineList": busbarNotRepeatLineList,
        "isBusBarRecover": isBusBarRecover,
        "isHeavyLoad": True,
        "isAreaDifferent": True,
        "isImportantUserSingle": True,
        "isImportantUserSuperSingle": True,
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
                "weight": userNumberWeight
            },
            "importantUserNumberObjective": {
                "unit": 1,
                "weight": 0
            }
        }
    }

    # response = create_plan_nn(vm)

