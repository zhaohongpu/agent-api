import requests
import json
import time
from common import get_path, set_cache, get_cache, is_mock_third_api, logger


# 浙达需要的是D5000的ID，南瑞是调控云ID，需要转换
def get_map_id(cloud_id):
    id_mapping = {
        "120131011500000245": "116530642052710942",
        "120131011500001436": "116530642052710963",
        "120131011500039932": "116530642052710450",
        "120131011500000243": "116530642052710940",
        "130131011500000588": "115404742145868659",
        "130131011500000589": "115404742145868661",
        "130131011500000590": "115404742145868660",
        "131131011500000396": "117093592006132181",
        "131131011500000395": "117093592006132180",
        "130131011500002776": "115404742145869029",
        "130131011500000532": "115404742145868577",
        "130131011500000533": "115404742145868579",
        "130131011500000534": "115404742145868578",
        "131131011500000359": "117093592006132139",
        "131131011500000360": "117093592006132140",
        "131131011500002846": "117093592006132334",
        "130131000000000850": "115404740971463751",
        "130131000000000851": "115404740971463750",
        "130131000000000852": "115404740971463749",
        "130131000000000849": "115404740971463752",
        "131131000000000501": "117093590831727068",
        "131131000000000502": "117093590831727069",
        "131131000000000503": "131131000000000502",
        "131131011500000146": "117093592006131871",
        "131131011500000147": "117093592006131872",
        "01123100000061": "113997366087909423",
        "01123101150142": "113997367262314858",
        "01123101150158": "113997367262314902",
        "01123101150061": "113997367262314626",
    }

    map_id = id_mapping.get(cloud_id)

    if map_id is None:
        return ""
    else:
        return map_id


def create_plan_nn(json_str):
    if isinstance(json_str, dict):
        json_str = json.dumps(json_str, ensure_ascii=False)

    url = "http://10.131.244.213:10018/api/dispatchAccidentPreplanThree/getAccidentPreplanNn"

    headers = {
        'Content-Type': 'application/json'
    }

    set_cache('api_create_plan_nn_input', json_str)

    if is_mock_third_api():
        with open(get_path('/demo/plan_nn.json'), 'r') as f:
           str = f.read()
           return json.loads(str)

    startTime = int(time.time())
    response = requests.post(url, json_str, headers=headers)
    cost = int(time.time()) - startTime

    response = json.loads(response.content)
    set_cache('api_create_plan_nn_output', response)

    message = response.get("message", "")
    logger.info(f"zheda api_create_plan_nn cost[{cost}s] input[{json_str}] output[{message}]")

    return response

def create_plan_n1(json_str):
    if isinstance(json_str, dict):
        json_str = json.dumps(json_str, ensure_ascii=False)

    url = "http://10.131.244.213:10018/api/dispatchAccidentPreplanThree/getAccidentPreplanN1Tran"

    headers = {
        'Content-Type': 'application/json'
    }

    set_cache('api_create_plan_n1_input', json_str)

    if is_mock_third_api():
        with open(get_path('/demo/plan_n1.json'), 'r') as f:
           str = f.read()
           return json.loads(str)

    response = requests.post(url, json_str, headers=headers)
    response = json.loads(response.content)
    set_cache('api_create_plan_n1_output', response)

    return response


if __name__ == "__main__":
    json_string = '{"type":"N-N","subId":"113997367262314498","maintDevice":[],"busbarReceiveLineList":[],"faultLineList":[],"notPjLineList":[],"beginDate":"2024-08-02","endDate":"2024-08-02","beginTime":"00:00:00","endTime":"23:59:59","dtFileTime":null,"joinCutType":null,"lineLoadRateThreshold":100,"loadRateSetupDTOList":[],"isYaoKong":true,"busbarRepeatLineList":[],"busbarNotRepeatLineList":[],"isBusBarRecover":true,"isHeavyLoad":false,"isAreaDifferent":true,"isImportantUserSingle":true,"isImportantUserSuperSingle":true,"mathematicalObjective":{"loadObjective":{"unit":10,"weight":100},"userLoadObjective":{"unit":10,"weight":500},"areaNumObjective":{"unit":1,"weight":20},"notYaoKongNumObjective":{"unit":1,"weight":10},"yaoKongNumObjective":{"unit":1,"weight":1},"userNumberObjective":{"unit":10,"weight":0},"importantUserNumberObjective":{"unit":1,"weight":0}}}'
    response = create_plan_nn(json_string)
    data = json.dumps(response, ensure_ascii=False)

    print(data)

    json_string = '{"type":"N-1","subId":"113997367262314902","maintDevice":[{"type":"TRAN","devIdList":["117093592006132180"],"text":"1号主变"}],"busbarReceiveLineList":[{"busbarId":null,"busbarName":null,"oppositeLineId":null,"oppositeLineName":null,"openPoint":null,"devId":null,"devName":null},{"busbarId":null,"busbarName":null,"oppositeLineId":null,"oppositeLineName":null,"openPoint":null,"devId":null,"devName":null},{"busbarId":null,"busbarName":null,"oppositeLineId":null,"oppositeLineName":null,"openPoint":null,"devId":null,"devName":null},{"busbarId":null,"busbarName":null,"oppositeLineId":null,"oppositeLineName":null,"openPoint":null,"devId":null,"devName":null}],"faultLineList":[],"notPjLineList":[],"beginDate":"2024-08-02","endDate":"2024-08-02","beginTime":"00:00:00","endTime":"23:59:59","dtFileTime":null,"joinCutType":null,"lineLoadRateThreshold":100,"loadRateSetupDTOList":[],"isHeavyLoad":false,"isYaoKong":true,"isAreaDifferent":true,"isImportantUserSingle":true,"isImportantUserSuperSingle":true,"busbarRepeatLineList":[],"busbarNotRepeatLineList":[],"isBusBarRecover":true,"mathematicalObjective":{"loadObjective":{"unit":10,"weight":100},"userLoadObjective":{"unit":10,"weight":500},"areaNumObjective":{"unit":1,"weight":20},"notYaoKongNumObjective":{"unit":1,"weight":10},"yaoKongNumObjective":{"unit":1,"weight":1},"userNumberObjective":{"unit":10,"weight":0},"importantUserNumberObjective":{"unit":1,"weight":0}}}'
    json_string = '{"type":"N-1","subId":"113997367262314902","maintDevice":[{"type":"TRAN","devIdList":["117093592006132181"],"text":"2号主变"}],"busbarReceiveLineList":[{"busbarId":null,"busbarName":null,"oppositeLineId":null,"oppositeLineName":null,"openPoint":null,"devId":null,"devName":null},{"busbarId":null,"busbarName":null,"oppositeLineId":null,"oppositeLineName":null,"openPoint":null,"devId":null,"devName":null},{"busbarId":null,"busbarName":null,"oppositeLineId":null,"oppositeLineName":null,"openPoint":null,"devId":null,"devName":null},{"busbarId":null,"busbarName":null,"oppositeLineId":null,"oppositeLineName":null,"openPoint":null,"devId":null,"devName":null}],"faultLineList":[],"notPjLineList":[],"beginDate":"2024-08-02","endDate":"2024-08-02","beginTime":"00:00:00","endTime":"23:59:59","dtFileTime":null,"joinCutType":null,"lineLoadRateThreshold":100,"loadRateSetupDTOList":[],"isHeavyLoad":false,"isYaoKong":true,"isAreaDifferent":true,"isImportantUserSingle":true,"isImportantUserSuperSingle":true,"busbarRepeatLineList":[],"busbarNotRepeatLineList":[],"isBusBarRecover":true,"mathematicalObjective":{"loadObjective":{"unit":10,"weight":100},"userLoadObjective":{"unit":10,"weight":500},"areaNumObjective":{"unit":1,"weight":20},"notYaoKongNumObjective":{"unit":1,"weight":10},"yaoKongNumObjective":{"unit":1,"weight":1},"userNumberObjective":{"unit":10,"weight":0},"importantUserNumberObjective":{"unit":1,"weight":0}}}'
    response = create_plan_n1(json_string)
    data = json.dumps(response, ensure_ascii=False)

    print(data)