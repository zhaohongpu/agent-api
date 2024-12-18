import json

from common import get_path


def get_value(data, expression):
    # 将表达式按"."分割
    keys = expression.replace("$.", "").split(".")

    # 逐级解析表达式
    value = data
    for key in keys:
        if "[" in key:
            key, index = key.split("[")
            index = int(index.replace("]", ""))
            value = value[key][index]
        else:
            value = value[key]

    return value


def get_object(info, object):
    if '$ref' in object:
        return get_value(info, object['$ref'])

    return object


def get_group_score():
    return [
        {
            "zsnr": "重要用户",
            "score": 95
        },
        {
            "zsnr": "失电负荷",
            "score": 90
        },
        {
            "zsnr": "供电可靠性",
            "score": 80
        },
        {
            "zsnr": "操作数量",
            "score": 85
        }
    ]

def caculate_group_score(data):
    result = []
    group_dict = {
        "重要用户": ["影响重要负荷", "影响重要用户数", "影响重要用户供电结构"],
        "失电负荷": ["影响负荷", "影响用户数"],
        "供电可靠性": ["失电设备数", "失电设备容量", "对侧重过载"],
        "操作数量": ["操作次数"]
    }
    # 初始化每个组的扣分总和
    subtraction_score_sum = {group: 0 for group in group_dict}

    for item in data["schemeScoreDetails"]:
        zsnr_value = item["zsnr"]
        for group, zsnr_list in group_dict.items():
            if zsnr_value in zsnr_list:
                subtraction_score_sum[group] += item["subtractionScore"]

    # 计算每个组的最终分数并构建结果列表
    for group in group_dict:
        final_score = 100 - subtraction_score_sum[group]
        result.append({
            "zsnr": group,
            "score": int(final_score)
        })

    return result

def get_plan_nn_table_info(info, table):

    result = {}
    result['title'] = table['title']  # 标题
    result['conclusionText'] = table['conclusionText']  # 方案描述
    result['conclusionTwoText'] = table['conclusionTwoText']  # 故障描述
    result['schemeScore'] = table['schemeScore']  # 评价分数
    # result['groupScore'] = get_group_score()  # 评价分数分组
    result['groupScore'] = caculate_group_score(table)  # 评价分数分组

    detail = []
    for v in table['schemeScoreDetails']:
        detail.append({
            "zsnr": v['zsnr'],  # 评价指标
            "subtractionScore": v['subtractionScore'],  # 扣分
            "score": 100 - v['subtractionScore']  # 评分
        })

    result['schemeScoreDetails'] = detail

    result['recoverTable'] = {
        'title': table['recoverTable']['title'],
        'rowList': []
    }

    result['unableRecoverTable'] = {
        'title': table['unableRecoverTable']['title'],
        'rowList': []
    }

    for r in table['recoverTable']['rowList']:
        busbarDev = get_object(info, r['deviceData']['busbarDev'])
        r2 = {
            # 复电表格没有 类型 字段
            "subName": r.get('subName', ''),  # 厂站
            "busbarDevName": busbarDev['devNameRemoveSubName'],  # 母线名称
            "receiveLine": r['receiveLine'],  # 受进线路
            "userPowerAreaCount": r['userPowerAreaCount'],  # 用户数/台区数（受进线路）
            "thisSideLoad": r['thisSideLoad'],  # 本侧电流/额定电流
            "openPoint": r['openPoint'],  # 开口点
            "oppositeLine": r['oppositeLine'],  # 对侧线路
            "oppositeLoad": r['oppositeLoad'],  # 对侧电流/额定电流
            "recoverPowerLine": r['recoverPowerLine'],  # 复电线路
            "userPowerAreaCount2": r['userPowerAreaCount2'],  # 用户数/台区数（复电线路）
            "recoverLoad": r['recoverLoad'],  # 复电线路电流
            "accumulatedRecoverLoad": r['accumulatedRecoverLoad'],  # 累计复电
            "oppositeLineMaxLoad": r['oppositeLineMaxLoad'],  # 对侧线路最高负荷/负载率
            "oppositeTranMaxLoad": r['oppositeTranMaxLoad'],  # 对侧主变最高负荷/负载率
            "dateTime": r['dateTime']  # 时间
        }
        result['recoverTable']['rowList'].append(r2)

    # 失电母线	类型	本侧线路	用户数/台区数	本侧电流/额定电流	开口点	对侧线路	对侧线路电流/额定电流	对侧主变最高负荷/负载率	最大负荷时间
    for r in table['unableRecoverTable']['rowList']:
        busbarDev = get_object(info, r['deviceData']['busbarDev'])
        r2 = {
            "subName": r.get('subName', ''), # 厂站
            "busbarDevName": busbarDev['devNameRemoveSubName'],  # 母线名称
            "lx": r['lx'],  # 母线名称
            "receiveLine": r['receiveLine'],  # 受进线路
            "userPowerAreaCount": r['userPowerAreaCount'],  # 用户数/台区数（受进线路）
            "thisSideLoad": r['thisSideLoad'],  # 本侧电流/额定电流
            "openPoint": r['openPoint'],  # 开口点
            "oppositeLine": r.get('oppositeLine', ''),  # 对侧线路
            "oppositeLoad": r.get('oppositeLoad', ''),  # 对侧电流/额定电流
            "oppositeTranMaxLoad": r.get('oppositeTranMaxLoad', ''),  # 对侧主变最高负荷/负载率
            "dateTime": r['maxLoadTime']  # 时间
        }
        result['unableRecoverTable']['rowList'].append(r2)

    return result

def get_plan_n1_table_info(info, plan):
    if plan is None:
        return None

    result = {}
    result['schemeScore'] = plan['schemeScore']
    # result['groupScore'] = get_group_score()  # 评价分数分组
    result['groupScore'] = caculate_group_score(plan)  # 评价分数分组
    result['type'] = plan['type']

    detail = []
    for v in plan['schemeScoreDetails']:
        detail.append({
            "zsnr": v['zsnr'],  # 评价指标
            "subtractionScore": v['subtractionScore'],  # 扣分
            "score": 100 - v['subtractionScore']  # 评分
        })

    result['schemeScoreDetails'] = detail
    result['transferTableGroupList'] = []

    for g in plan['transferTableGroupList']:
        group = {
            "title": g['title'],
            "conclusionText": g['conclusionText'], # 方案描述
            "transferTableList": []
        }

        for t in g['transferTableList']:
            table = {
                "title": t['title'],
                "rowList": []
            }

            #
            for r in t['rowList']:
                r2 = {
                    "subName": info.get('subName', ''),
                    "reduceLoadLine": r['reduceLoadLine'],  # 减载线路
                    "userPowerAreaCount": r['userPowerAreaCount'],  # 用户数/台区数（受进线路）
                    "thisSideLoad": r['thisSideLoad'],  # 本侧电流/额定电流
                    "openPoint": r['openPoint'],  # 开口点
                    "oppositeLine": r['oppositeLine'],  # 对侧线路
                    "oppositeLoad": r['oppositeLoad'],  # 对侧电流/额定电流
                    "oppositeTranMaxLoad": r['oppositeTranMaxLoad'],  # 对侧主变最高负荷/负载率
                    "transferAfterSituation": r['transferAfterSituation'],  # 转移后重过载情况
                    "accumulatedReduceLoad": r['accumulatedReduceLoad'],  # 累计减载负荷
                    "reduceLoadAfterTranLoad": r['reduceLoadAfterTranLoad'],  # 减载后主变负荷/负载率
                }
                table['rowList'].append(r2)

            group['transferTableList'].append(table)

        result['transferTableGroupList'].append(group)

    return result


def get_plan_single_table_info(info, plan):
    if plan is None:
        return None

    result = {
        "lineAndAndOppositeLines": []
    }

    for r in plan['lineAndAndOppositeLines']:
        r2 = {
            "subName": info.get('subName', ''),
            "busbarDevName": r['busbarDev']['devNameRemoveSubName'],  # 母线名称
            "receiveLine": r['thisLineDeviceDto']['devNameRemoveSubName'],  # 受进线路
            "thisBreak": r['thisBreakDev']['devNameRemoveSubName'],  # 本侧开关
            "openPoint": r['openPoint'],  # 开口点
            "oppositeBreak": r['oppositeBreakDev']['devNameRemoveSubName'],  # 本侧开关
            "oppositeLine": r['oppositeLineDeviceDto']['devNameRemoveSubName'],  # 对侧线路
            "oppositeWind": r['oppositeWindDeviceDto']['devNameRemoveSubName'],  # 对侧主变
            "oppositeWindLoad": "%.2fA/%.2f" % (r['oppositeWindDeviceDto']['devImax'], r['oppositeWindDeviceDto']['devLoadRate']) + '%',
            # 对侧主变最高负荷/负载率
        }
        result['lineAndAndOppositeLines'].append(r2)

    return result


def get_plan_nn_info(info):
    table1 = get_plan_nn_table_info(info, info["recoverAndUnableRecoverTable1"])
    table2 = get_plan_nn_table_info(info, info["recoverAndUnableRecoverTable2"])
    table3 = get_plan_nn_table_info(info, info["recoverAndUnableRecoverTable3"])

    return {
        "recoverAndUnableRecoverTable1": table1,
        "recoverAndUnableRecoverTable2": table2,
        "recoverAndUnableRecoverTable3": table3,
    }

def get_plan_n1_info(info):
    return {
        "plan1": get_plan_n1_table_info(info, info['plan1']),
        "plan2": get_plan_n1_table_info(info, info['plan2'])
    }

def get_plan_single_info(info):
    return {
        "plan1": get_plan_single_table_info(info, info['plan1']),
        "plan2": get_plan_single_table_info(info, info['plan2'])
    }

if __name__ == "__main__":
    with open(get_path('/demo/plan_nn.json'), 'r', encoding='utf-8') as f:
        data = f.read()
        data = json.loads(data)
        info = get_plan_nn_info(data['data'])
        print(info)

    with open(get_path('/demo/plan_n1.json'), 'r', encoding='utf-8') as f:
        str = f.read()
        str = json.loads(str)
        info = get_plan_n1_info(str['data'])
        print(json.dumps(info, ensure_ascii=False))

        info = get_plan_single_info(str['data'])
        print(json.dumps(info, ensure_ascii=False))
