from common import *
from service.plan import PlanService
from third.dfe.api import *
from third.kedong.api import *


class FaultService:

    @staticmethod
    def get_fault(event_id=None):
        fault = get_file("/data/fault_by_event_id/%s.json" % event_id, return_json=True)
        return fault

    @staticmethod
    def post_fault_to_dfe(event_id=None, fault=None):
        """
        投送故障信息给东方电子，用于成图
        :param event_id:
        :param fault:
        :return:
        """
        post_fault_info(event_id, fault)

    @staticmethod
    def get_desc_text(fault):
        # text = "2024年9月20日，10:00:00  220kV 申江站35kV III母线母差保护动作，2号主变35kV开关分闸，35kV III母故障失电。根据保护动作及开关变位情况初步判定为35kV III母线及其附属设备故障。需要通知中心站、线路操作班、用电监察等去现场检查。"
        fault_sec_value = fault["fault_list"][0]["fault_sec"]
        dt_object = datetime.datetime.fromtimestamp(fault_sec_value)
        formatted_time = dt_object.strftime('%Y-%m-%d %H:%M')

        fac01_name = fault["fault_list"][0]["fac01_name"]
        fac01_name = fac01_name if fac01_name else '未知场站'

        dev_name = fault["fault_list"][0]["dev_name"]
        dev_name = dev_name if dev_name else '未知设备'

        text = """%s %s站%s故障""" % (formatted_time, fac01_name, dev_name)

        brick_text = []
        for brick in fault["fault_list"][0]["brk_data_list"]:
            if brick['brk_status'] == 1: # 暂只取分闸信息
                continue

            status = "合闸" if brick['brk_status'] == 1 else "分闸"
            brick_text.append(f"{brick['brk_name']}{status}")

        if brick_text:
            text += "，"
            text += "、".join(brick_text)

        text += "，根据保护动作及开关变位情况初步判定为%s故障。" % dev_name

        # 科东信息
        kedong_data = get_notify_info(fault)
        if 'result' in kedong_data:
            send_department = kedong_data["result"]["send_department"]
            if '需要通知' not in send_department:
                send_department = '需要通知' + send_department

            check_place = kedong_data["result"]["check_place"]
            text = text + send_department + check_place + "。"

        return text

    @staticmethod
    def get_off_vec_text_list(fault, type):
        """
        按type返回停电设备列表
        :param fault:
        :param type:
        :return:
        """
        name_list = []
        try:
            for v in fault['trans_off_fault'][0]['off_vec']:
                if v['dev_type'] == type:
                    name_list.append("%s%s" % (v['fac_name'], v['dev_name']))
        except Exception as e:
            return name_list

        return name_list

    @staticmethod
    def get_off_vec_map(fault):
        map = {}
        #try:
        for v in fault['trans_off_fault'][0]['off_vec']:
            dev_type = v['dev_type']
            if dev_type == 1210:  # 线端视为线路
                dev_type = 1201
            if dev_type not in map:
                map[dev_type] = {}

            fac_name = v['fac_name']
            if fac_name not in map[dev_type]:
                map[dev_type][fac_name] = {}

            vl_type = v['vl_type']
            if vl_type not in map[dev_type][fac_name]:
                map[dev_type][fac_name][vl_type] = []

            map[dev_type][fac_name][vl_type].append(v['dev_name'])
        #except Exception as e:
        #    logger.info(e)
        #    return map

        return map

    @staticmethod
    def get_off_vec_text_list_group_by_fac_name(fault, type):
        """
        停电设备列表按场站分组
        :param fault:
        :param type:
        :return:
        """
        name_list = {}
        try:
            for v in fault['trans_off_fault'][0]['off_vec']:
                if v['dev_type'] != type:
                    continue

                name = "%s%dKV" % (v['fac_name'], v['vl_type'])
                if name not in name_list:
                    name_list[name] = []

                name_list[name].append(v['dev_name'])
        except Exception as e:
            return name_list

        return name_list

    @staticmethod
    def get_bzt_name_list(fault):
        """
        备自投名称列表
        :param fault:
        :return:
        """
        name_list = []
        try:
            for v in fault['fault_list'][0]['bzt_data_list']:
                name_list.append(v['st_name'])
        except Exception as e:
            return name_list

        return name_list

    @staticmethod
    def get_evaluate_info(fault):
        try:
            return fault['trans_off_fault'][0]['evaluate_info'][0]
        except Exception as e:
            return None

    # 全停站
    @staticmethod
    def get_stop_all_station(fault):
        try:
            return fault['trans_off_fault'][0]['lost_st_vec'][0]
        except Exception as e:
            return None

    # 重过载站
    @staticmethod
    def get_overload_station(fault):
        try:
            return fault['trans_off_fault'][0]['over_vec'][0]
        except Exception as e:
            return None

    # 重过载引起原因站（生成转供需要）
    @staticmethod
    def get_overload_reason_station(fault, overload_st):
        try:
            for v in fault['trans_off_fault'][0]['off_vec']:
                if v['dev_type'] == 1311 and v['fac_name'] == overload_st['st_name']:
                    return v
        except Exception as e:
            return None

        return None

    # 单电源站
    @staticmethod
    def get_single_source_station(fault):
        try:
            for v in fault['trans_off_fault'][0]['risk_vec']:
                if v['weaktype'] == '厂站单主变':
                    return v
            return None
        except Exception as e:
            return None

    # 单电源引起原因站（生成转供需要）
    @staticmethod
    def get_single_source_reason_station(fault, single_source_st):
        try:
            for v in fault['trans_off_fault'][0]['off_vec']:
                if v['dev_type'] == 1311 and v['fac_name'] == single_source_st['st_name']:
                    return v

            return None
        except Exception as e:
            return None

    # 重要用户
    @staticmethod
    def get_important_user(fault):
        try:
            return fault['trans_off_fault'][0]['user_vec'][0]
        except Exception as e:
            return None

    @staticmethod
    def get_analysis_text(fault):
        # 全停站
        stop_all_station = FaultService.get_stop_all_station(fault=fault)

        # 失电设备分析
        fault_text_list = []

        off_map = FaultService.get_off_vec_map(fault=fault)
        logger.info(f"off_map[{off_map}] len[{len(off_map)}]")

        dev_types = [
            {"type":1301,"name":"母线","unit":"条"},
            {"type":1311,"name": "主变","unit":"个"},
            {"type":1201,"name": "线路","unit":"条"},
            {"type":408,"name": "馈线","unit":"条"}
        ]

        for t in dev_types:
            if t['type'] in off_map:
                for fac_name, vl_map in off_map[t['type']].items():
                    str2 = f"{fac_name}"
                    for vl_type, list in vl_map.items():
                        str2 += f"{len(list)}{t['unit']}{vl_type}KV{t['name']}失电({','.join(list)})"
                        fault_text_list.append(str2)

        # 失电负荷分析
        load_text_list = []

        # 馈线
        kuixian_name_list = FaultService.get_off_vec_text_list_group_by_fac_name(fault, 408)
        if kuixian_name_list:
            for k, v in kuixian_name_list.items():
                text = "%s%d条馈线失电(%s)" % (k, len(v), ",".join(v))
                load_text_list.append(text)

        # 供电可靠性分析
        effect_text_list = []

        if stop_all_station:
            text = "%s全站失电" % (stop_all_station['st_name'])
            effect_text_list.append(text)

        signal_source_dev = FaultService.get_single_source_station(fault)
        signal_source_reason_dev = FaultService.get_single_source_reason_station(fault, signal_source_dev)
        # text = "%s%s失电，导致%s单电源" % (signal_source_reason_dev['fac_name'], signal_source_reason_dev['dev_name'], signal_source_dev['dev_name'])
        if signal_source_dev and signal_source_reason_dev:
            text = "%s%s失电，导致单电源问题(%s)" % (signal_source_reason_dev['fac_name'], signal_source_reason_dev['dev_name'], signal_source_dev['dev_name'])
            effect_text_list.append(text)

        overload_dev = FaultService.get_overload_station(fault)
        overload_reason_dev = FaultService.get_overload_reason_station(fault, overload_dev)
        if overload_dev and overload_reason_dev:
            text = "%s%s失电，导致重过载问题(%s：%.2f%%)" % (overload_reason_dev['fac_name'], overload_reason_dev['dev_name'], overload_dev['warn_dev_name'],
                                        overload_dev['warn_value'] / overload_dev['warn_set'] * 100)
            effect_text_list.append(text)
        elif overload_dev:
            text = "%s%s重过载(%.2f%%)" % (
            overload_dev['st_name'], overload_dev['warn_dev_name'],
            overload_dev['warn_value'] / overload_dev['warn_set'] * 100)
            effect_text_list.append(text)

        user_text_list = []
        user = FaultService.get_important_user(fault)
        if user:
            data = get_vip_info(str(fault['fault_list'][0]['event_id']))

            if 'data' in data:
                for v in data['data']:
                    if v['vipName'] == user['vip_name']:
                        text = "%s%s(%d级重要用户，%s)" % (v['vipName'], user['load_type'], user['load_level'], v['result'])
                        user_text_list.append(text)
                        break

        list2 = []
        if fault_text_list:
            list2.append("，".join(fault_text_list))

        # if load_text_list:
        #     list2.append("，".join(load_text_list))

        if effect_text_list:
            list2.append("，".join(effect_text_list))

        desc = "；".join(list2)
        output = """【失电设备分析】
%s

【重要用户分析】
%s

【供电可靠性分析(待解决故障列表)】
%s

""" % (
        "\n".join(fault_text_list), "\n".join(user_text_list), "\n".join(effect_text_list))

        if not effect_text_list:
            desc = "当前故障，智能体暂不支持进一步处理。"
            output += desc
        elif len(off_map) == 1 and 408 in off_map:
            output += "仅有馈线失电，智能体暂不支持进一步处理。"
        else:
            output += "针对以上故障情况，是否调用负荷转供组件生成转供方案？"

        result = {
            'send_text': desc,
            'api_text': output
        }

        return result
