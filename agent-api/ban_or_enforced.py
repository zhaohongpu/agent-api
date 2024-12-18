import re
from common import get_file, set_cache

oppositeLineId_map = get_file('./demo/lineload_map.json', return_json=True)
busbarId_map = get_file('./demo/busbar_map.json', return_json=True)
def get_oppositeLineId(station_name):
    for key, value in oppositeLineId_map.items():
        if key == station_name:
            return value
    return None

def get_busbarId(subName, station_name):
    if subName in busbarId_map:
        for key, value in busbarId_map[subName].items():
            if key == station_name:
                return value
    return None

def extract_name(name):
    """提取站名并去除可能的‘站’字"""
    if "站" in name:
        return name.split('站')[1]
    return name.strip()

def extract_three_params(text, subName):

    text = text.replace('千伏', 'kv').replace('kV', 'kv').replace('KV', 'kv')
    text = text.replace(subName, '')

    if "通过恢复" in text and "倒送" in text:
        result = re.split(r'通过恢复|倒送', text)
        result = [segment.strip() for segment in result if segment.strip()]
        oppositeLineName = extract_name(result[0].split('，')[-1].split('。')[-1].split('；')[-1])
        devName = extract_name(result[1] if len(result) > 1 else "")
        busbarName = extract_name(result[-1].split('，')[0].split('。')[0].split('；')[0])

        oppositeLinedict = {
            'oppositeLineName': oppositeLineName,
            'oppositeLineId': get_oppositeLineId(oppositeLineName)
        }
        devdict = {
            'devName': devName,
            'devId': get_oppositeLineId(devName)
        }
        busbardict = {
            'busbarName': busbarName,
            'busbarId': get_busbarId(subName, busbarName)
        }

        lst = [oppositeLinedict, devdict, busbardict]

    else:
        lst = []

    return lst

def is_ban_or_enforced(raw_query, subName):
    try:
        pattern = r'[\s，。！？；：]+'
        text_lst = re.split(pattern, raw_query)
        text_lst = [text for text in text_lst if "通过恢复" in text and "倒送" in text]
        busbarRepeatLineList = []
        busbarNotRepeatLineList = []

        for text in text_lst:
            if "禁止" in text:
                text_split = text.split("禁止")
                enforce_text = text_split[0]
                ban_text = text_split[1]
            else:
                enforce_text = text
                ban_text = ""
            busbarRepeatLine = extract_three_params(enforce_text, subName)
            busbarRepeatLineList.append(busbarRepeatLine)
            busbarNotRepeatLine = extract_three_params(ban_text, subName)
            busbarNotRepeatLineList.append(busbarNotRepeatLine)

        busbarNotRepeatLineList = [item for sublist in busbarNotRepeatLineList for item in sublist]
        busbarRepeatLineList = [item for sublist in busbarRepeatLineList for item in sublist]

        return busbarNotRepeatLineList, busbarRepeatLineList
    except Exception as e:
        set_cache('ban_or_enforced_params_info_output', str(e))
        return [], []

if __name__ == "__main__":
    # raw_query = "横沔站失电，生成专供方案"
    # raw_query = "横沔站失电，生成专供方案，横沔站创37康新通过恢复横沔站横22火箭倒送10kV二、三段母线"
    # raw_query = "横沔站失电，生成专供方案，禁止杉18御水通过恢复横32沿北倒送10kV四段母线"
    # raw_query = "横沔站失电，生成专供方案，禁止杉18御水通过恢复横32沿北倒送10kV四段母线，禁止杉18御水通过恢复横32沿北倒送10kV四段母线，创37康新通过恢复横22火箭倒送10kV二、三段母线，自动优化，优化2轮。"
    raw_query = "横沔站失电，生成专供方案，横沔站杉18御水通过恢复横32沿北倒送10kV四段母线，禁止创37康新通过恢复横22火箭倒送10kV二、三段母线，自动优化，优化2轮。"
    # raw_query = "横沔站失电，生成专供方案，迪士尼站尼31瓦屑通过恢复横沔站横27老镇倒送横沔站10kV二、三段母线。"

    subName = "横沔站"
    busbarNotRepeatLineList, busbarRepeatLineList = is_ban_or_enforced(raw_query, subName)
    # busbarNotRepeatLineList = is_prohibited_or_enforced(raw_query, subName)
    # isRepeatLine = is_RepeatLine(subName, raw_query)

    print(">>>>>>>>>>>>>>>>>>>>>> 最终输出结果 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    print(">busbarRepeatLineList:", busbarRepeatLineList)
    print(">busbarNotRepeatLineList", busbarNotRepeatLineList)



