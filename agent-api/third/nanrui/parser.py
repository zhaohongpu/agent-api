
def decode(byte_sequence):
    if isinstance(byte_sequence, bytes):
        try:
            chinese_string = byte_sequence.decode('gbk')
            return chinese_string
        except Exception as e:
            return "decode_error"
    else:
        return byte_sequence


# 重过载站
def get_overload_station(fault):
    return fault['trans_off_fault'][0]['over_vec'][0]

# 重过载引起原因站（生成转供需要）
def get_overload_reason_station(fault, overload_st):
    for v in fault['trans_off_fault'][0]['off_vec']:
        if v['dev_type'] == 1311 and v['fac_name'] == overload_st['st_name']:
            return v

    return None

def pb2dict(fault_info_list):
    info = {
        "system_name": decode(fault_info_list.system_name),  # 1
        "fault_num": decode(fault_info_list.fault_num),   # 2
        "type": decode(fault_info_list.type),  # 3
        "fault_list": [],  # 4
        "trans_off_fault": [],  # 5
    }

    for data in fault_info_list.fault_list:
        fault_info = {
            "event_id": decode(data.event_id),  # 1
            "fault_sec": decode(data.fault_sec),
            "fault_msec": decode(data.fault_msec),
            "fault_dev": decode(data.fault_dev),
            "dev_name": decode(data.dev_name),
            "fault_phase": decode(data.fault_phase),
            "reclose_stat": decode(data.reclose_stat),
            "fault_dis_01": decode(data.fault_dis_01),
            "fault_dis_02": decode(data.fault_dis_02),
            "fault_cur_01": decode(data.fault_cur_01),
            "fault_cur_02": decode(data.fault_cur_02),
            "seq_fac01": decode(data.seq_fac01),
            "seq_fac02": decode(data.seq_fac02),
            "fac01_name": decode(data.fac01_name),
            "fac02_name": decode(data.fac02_name),
            "soe_event_id": decode(data.soe_event_id),
            "pmu_event_id": decode(data.pmu_event_id),
            "relay_act_info": decode(data.relay_act_info),
            "path": decode(data.path),
            "is_ack": decode(data.is_ack),
            "describe": decode(data.describe),
            "voltage_type": decode(data.voltage_type),
            "ln_nodes": [],
            "brk_data_list": [],
            "relay_data_list": [],
            "bzt_data_list": [],
            "zy_data_list": [],  # 27
        }

        for v in data.ln_nodes:
            fault_info["ln_nodes"].append(decode(v))

        for v in data.brk_data_list:
            brk_data = {
                "fault_time": decode(v.fault_time),  # 1
                "fault_msec": decode(v.fault_msec),
                "fac_id": decode(v.fac_id),
                "brk_id": decode(v.brk_id),
                "brk_name": decode(v.brk_name),
                "brk_status": decode(v.brk_status),
                "sig_type": decode(v.sig_type),
                "brk_phase": decode(v.brk_phase),
                "event_id": decode(v.event_id),
                "ana_sta": decode(v.ana_sta)  # 10
            }
            fault_info["brk_data_list"].append(brk_data)

        for v in data.relay_data_list:
            relay_data = {
                "fault_time": decode(v.fault_time),  # 1
                "fault_msec": decode(v.fault_msec),
                "fac_id": decode(v.fac_id),
                "relay_id": decode(v.relay_id),
                "dev_id": decode(v.dev_id),
                "relay_name": decode(v.relay_name),
                "status": decode(v.status),
                "sig_type": decode(v.sig_type),
                "event_id": decode(v.event_id),
                "ana_sta": decode(v.ana_sta)  # 10
            }
            fault_info["relay_data_list"].append(relay_data)

        for v in data.bzt_data_list:
            bzt_data = {
                "event_id": decode(v.event_id),   # 1
                "act_time": decode(v.act_time),
                "msec": decode(v.msec),
                "bzt_id": decode(v.bzt_id),
                "bzt_name": decode(v.bzt_name),
                "st_id": decode(v.st_id),
                "st_name": decode(v.st_name),
                "vl_type": decode(v.vl_type),
                "is_succ": decode(v.is_succ),
                "brk_id": decode(v.brk_id),
                "brk_name": decode(v.brk_name),
                "brk_status": decode(v.brk_status)  # 12
            }
            fault_info["bzt_data_list"].append(bzt_data)

        for v in data.zy_data_list:
            zy_data = {
                "event_id": decode(v.event_id),  # 1
                "act_time": decode(v.act_time),
                "msec": decode(v.msec),
                "zy_id": decode(v.zy_id),
                "zy_name": decode(v.zy_name),
                "st_id": decode(v.st_id),
                "st_name": decode(v.st_name),
                "vl_type": decode(v.vl_type),
                "is_succ": decode(v.is_succ),
                "brk_id": decode(v.brk_id),
                "brk_name": decode(v.brk_name),
                "brk_status": decode(v.brk_status)  # 12
            }
            fault_info["zy_data_list"].append(zy_data)

        info["fault_list"].append(fault_info)

    for data in fault_info_list.trans_off_fault:
        trans_off_fault = {
            "evaluate_info": [],  # 1
            "off_vec": [],
            "risk_vec": [],
            "user_vec": [],
            "over_vec": [],
            "lost_st_vec": []  # 6
        }

        for v in data.evaluate_info:
            evaluate_info = {
                "event_id": decode(v.event_id),  # 1
                "fault_dev": decode(v.fault_dev),
                "fault_sec": decode(v.fault_sec),
                "fault_level": decode(v.fault_level),
                "fault_desc": decode(v.fault_desc),
                "rule_desc": decode(v.rule_desc),
                "lost_load": decode(v.lost_load),
                "lost_per": decode(v.lost_per),
                "load_before": decode(v.load_before),
                "power_off_num": decode(v.power_off_num),
                "power_off_per": decode(v.power_off_per),
                "effect_vip": decode(v.effect_vip),
                "lost_st_num": decode(v.lost_st_num),
                "lost_bus_num": decode(v.lost_bus_num),
                "update_sec": decode(v.update_sec),
                "source_system": decode(v.source_system),
                "report_level": decode(v.report_level),
                "report_rule_desc": decode(v.report_rule_desc),
                "lost_city_load": decode(v.lost_city_load)  # 19
            }
            trans_off_fault["evaluate_info"].append(evaluate_info)

        for v in data.off_vec:
            off_vec = {
                "event_id": decode(v.event_id),  # 1
                "off_dev": decode(v.off_dev),
                "dev_name": decode(v.dev_name),
                "vl_type": decode(v.vl_type),
                "fac_type": decode(v.fac_type),
                "fac_name": decode(v.fac_name),
                "first_st": decode(v.first_st),
                "second_st": decode(v.second_st),
                "dev_type": decode(v.dev_type),
                "is_restore": decode(v.is_restore),
                "p": decode(v.p),
                "ln_nodes": []  # 12
            }

            for n in v.ln_nodes:
                off_vec["ln_nodes"].append(decode(n))

            trans_off_fault["off_vec"].append(off_vec)

        for v in data.risk_vec:
            risk_vec = {
                "event_id": decode(v.event_id),  # 1
                "risk_dev": decode(v.risk_dev),
                "dev_name": decode(v.dev_name),
                "st_id": decode(v.st_id),
                "st_name": decode(v.st_name),
                "weaktype": decode(v.weaktype),
                "lost_power": decode(v.lost_power),
                "vl": decode(v.vl),
                "is_new": decode(v.is_new)  # 9
            }
            trans_off_fault["risk_vec"].append(risk_vec)

        for v in data.user_vec:
            user_vec = {
                "event_id": decode(v.event_id),  # 1
                "off_dev": decode(v.off_dev),
                "dev_name": decode(v.dev_name),
                "fac_name": decode(v.fac_name),
                "vl_type": decode(v.vl_type),
                "vip_name": decode(v.vip_name),
                "load_level": decode(v.load_level),
                "load_type": decode(v.load_type)  # 8
            }
            trans_off_fault["user_vec"].append(user_vec)

        for v in data.over_vec:
            over_vec = {
                "event_id": decode(v.event_id),  # 1
                "warn_type": decode(v.warn_type),
                "warn_level": decode(v.warn_level),
                "warn_st": decode(v.warn_st),
                "st_name": decode(v.st_name),
                "warn_dev": decode(v.warn_dev),
                "warn_dev_name": decode(v.warn_dev_name),
                "warn_value": decode(v.warn_value),
                "warn_set": decode(v.warn_set),
                "fault_dev": decode(v.fault_dev),
                "fault_dev_name": decode(v.fault_dev_name),
                "voltage_type": decode(v.voltage_type),  # 12
            }
            trans_off_fault["over_vec"].append(over_vec)

        for v in data.lost_st_vec:
            lost_st_vec = {
                "event_id": decode(v.event_id),  # 1
                "st_id": decode(v.st_id),
                "st_name": decode(v.st_name),
                "vl_type": decode(v.vl_type),
                "is_restore": decode(v.is_restore),  # 5
            }
            trans_off_fault["lost_st_vec"].append(lost_st_vec)

        info["trans_off_fault"].append(trans_off_fault)

    return info