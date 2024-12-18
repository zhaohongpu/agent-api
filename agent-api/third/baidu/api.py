import json

import requests
import os
from common import to_json, logger

AB_URL_PREFIX = os.getenv("AB_URL_PREFIX", "http://25.45.24.127:8088/api/ai_apaas/v1")
AB_AUTH_STRING = os.getenv("AB_AUTH_STRING", "private|771cf7097e68409dbf23671d5da7ad96")
AB_APP_ID = os.getenv("AB_APP_ID", "efe6a312-c2c0-4f52-ae0d-81abf2d567ea")
AB_AUTH_HEADER = os.getenv("AB_AUTH_HEADER", "X-Authorization")


def create_conversation():
    url = "{}/app/conversation".format(AB_URL_PREFIX)
    header = {
        "Content-Type": "application/json",
        AB_AUTH_HEADER: "Bearer {}".format(AB_AUTH_STRING)
    }

    data = {
        "app_id": AB_APP_ID
    }

    response = requests.post(url, data=to_json(data), headers=header)
    response = json.loads(response.content)
    logger.info("create_conversation_api input:{} output:{}".format(data, response))
    return response

# 直接调用组件
def function_call(name, query, input={}, is_print_log=True):
    url = "{}/app/conversation/runs".format(AB_URL_PREFIX)
    header = {
        "Content-Type": "application/json",
        AB_AUTH_HEADER: "Bearer {}".format(AB_AUTH_STRING)
    }

    conversation = create_conversation()

    data = {
        "app_id": AB_APP_ID,
        "query": query,
        "stream": False,
        "conversation_id": conversation['conversation_id'],
        "tool_choice": {
            "type": "function",
            "function": {
                "name": name,
                "input": input
            }
        }
    }

    response = requests.post(url, data=to_json(data), headers=header)
    response = json.loads(response.content)
    if is_print_log:
        logger.info("function_call_api name[{}] input[{}] output:[{}]".format(name, data, response))

    return response

# 调用千帆大模型
def llm_call(query):
    url = "http://10.131.144.83:28080/apis/ais/sgcc"
    header = {
        "Content-Type": "application/json"
    }

    data = {"messages":[{"role":"user","content":query}]}

    response = requests.post(url, data=to_json(data), headers=header)
    response = json.loads(response.content)
    logger.info("llm_call query[ignore] output[{}]".format(response))
    return response


if __name__ == "__main__":
    query = 'False, 100, 80, False 方案描述: 有2台主变、4段母线，下级馈线可自切至站外馈线3条、直送用户数4条、重要用户进线0条、有转供路径的馈线0条、无转供路径的馈线24条'
    result = function_call('plan_search', query)
    print(result)

    query = """下面是一个需要调整的负荷转供方案，之后我会提供一组相似的负荷转供方案描述以及对应的调节策略，你需要综合判断方案的相似程度以及相同调节策略的数量，选择你的调节策略。
判断相似程度时，优先判断主变数量、母线段数量、下级馈线可自切至站外的馈线数量和直送用户数量。
============== 本方案 ================
有2台主变、4段母线，下级馈线可自切至站外馈线3条、直送用户数4条、重要用户进线0条、有转供路径的馈线0条、无转供路径的馈线24条
事故发生后0条馈线自切至站外不失电，失电用户数11723，通过倒送母线及一级转供恢复6652户用户，通过二级转供及电缆拼接复电0户用户，剩余5071户用户未复电
=====================================
下面是几组相似的转供方案，以及对应的调节策略
==========方案_4033_1410==========

有2台主变、4段母线，下级馈线可自切至站外馈线3条、直送用户数1条、重要用户进线0条、有转供路径的馈线0条、无转供路径的馈线20条
 事故发生后0条馈线自切至站外不失电，失电用户数33147，通过倒送母线及一级转供恢复18352户用户，通过二级转供及电缆拼接复电0户用户，剩余14795户用户未复电
调节策略:
**是否允许操作非遥控开关**: True
**复电用户数权重**：100
**线路过载限值**: 100
**是否允许母线复电**: False

==========方案_4118_3826==========

有2台主变、4段母线，下级馈线可自切至站外馈线4条、直送用户数0条、重要用户进线1条、有转供路径的馈线0条、无转供路径的馈线20条
事故发生后0条馈线自切至站外不失电，失电用户数10825，通过倒送母线及一级转供恢复3368户用户，通过二级转供及电缆拼接复电0户用户，剩余7457户用户未复电
调节策略:
**是否允许操作非遥控开关**: True
**复电用户数权重**：0
**线路过载限值**: 100
**是否允许母线复电**: False

==========方案_4139_3826==========

有2台主变、4段母线，下级馈线可自切至站外馈线4条、直送用户数2条、重要用户进线0条、有转供路径的馈线1条、无转供路径的馈线12条
事故发生后1条馈线自切至站外不失电，失电用户数22802，通过倒送母线及一级转供恢复4716户用户，通过二级转供及电缆拼接复电0户用户，剩余18079户用户未复电
调节策略:
**是否允许操作非遥控开关**: True
**复电用户数权重**：0
**线路过载限值**: 100
**是否允许母线复电**: False

==========方案_4225_3826==========

有3台主变、4段母线，下级馈线可自切至站外馈线4条、直送用户数3条、重要用户进线0条、有转供路径的馈线1条、无转供路径的馈线20条
事故发生后1条馈线自切至站外不失电，失电用户数24186，通过倒送母线及一级转供恢复7479户用户，通过二级转供及电缆拼接复电0户用户，剩余14964户用户未复电
调节策略:
**是否允许操作非遥控开关**: True
**复电用户数权重**：0
**线路过载限值**: 100
**是否允许母线复电**: False

==========方案_4184_1207==========

有2台主变、4段母线，下级馈线可自切至站外馈线3条、直送用户数0条、重要用户进线0条、有转供路径的馈线0条、无转供路径的馈线23条
事故发生后1条馈线自切至站外不失电，失电用户数15480，通过倒送母线及一级转供恢复6098户用户，通过二级转供及电缆拼接复电0户用户，剩余8400户用户未复电
调节策略:
**是否允许操作非遥控开关**: True
**复电用户数权重**：100
**线路过载限值**: 100
**是否允许母线复电**: True



请你首先判断哪个方案与本方案最相似，再根据相似方案的调节策略决定本方案的调节策略。
输出中需要包含思考过程、相似方案编号和参数的调整策略。

以下是一个输出样例：
```json
{
    "思考过程": "方案_18与本方案相似程度最高，因此选择方案_18的调节策略",
    "相似方案编号": "方案_18",
    "调整参数":
    {
        "是否允许操作非遥控开关": True,
        "复电用户数权重": 100,
        "线路过载限值": 100,
        "是否允许母线复电": True
    }
}
```"""

    result = llm_call(query)
    print(result)
