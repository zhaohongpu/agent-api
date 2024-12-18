import os
from common import *
from service.fault import FaultService
import datetime

# 指定要遍历的顶级目录
dir = '/temp/pudong'

if __name__ == '__main__':
    # 遍历目录
    for filenames in os.walk(get_path(dir)):
        for filename in filenames:
            for file in filename:
                if file.endswith('.json'):
                    file = f"{dir}/{file}"
                    f = get_file(file, return_json=True)

                    start_timestamp = datetime.datetime.utcfromtimestamp(f['fault_list'][0]['fault_sec'] + 8 * 3600)
                    datetime2 = start_timestamp.strftime('%Y-%m-%d %H:%M:%S')

                    stop = FaultService.get_stop_all_station(f)

                    dev_name = f['fault_list'][0]['dev_name']
                    dev_id = f['fault_list'][0]['fault_dev']

                    fac_name = f['fault_list'][0]['fac01_name']
                    relay_act_info = f['fault_list'][0]['relay_act_info']

                    lost_st_vec = f['trans_off_fault'][0]['lost_st_vec']
                    off_vec = f['trans_off_fault'][0]['off_vec']
                    over_vec = f['trans_off_fault'][0]['over_vec']
                    risk_vec = f['trans_off_fault'][0]['risk_vec']
                    user_vec = f['trans_off_fault'][0]['user_vec']

                    over = FaultService.get_overload_station(f)
                    over_tag = '1' if over is not None else '0'

                    over_reason = FaultService.get_overload_reason_station(f, over)
                    over_reason_tag = '1' if over_reason is not None else '0'

                    single = FaultService.get_single_source_station(f)
                    single_reason = FaultService.get_single_source_reason_station(f, single_source_st=single)

                    single_tag = '1' if single is not None else '0'
                    single_reason_tag = '1' if single_reason is not None else '0'

                    ev_info = FaultService.get_evaluate_info(f)

                    event_id = f['fault_list'][0]['event_id']

                    key = f"[{datetime2}] event_id:{event_id} num:{f['fault_num']}_level:{ev_info['fault_level']}_st:{len(lost_st_vec)}_off:{len(off_vec)}_risk:{len(risk_vec)}_user:{len(user_vec)}_over:{len(over_vec)}_over_reason:{over_reason_tag}_sin:{single_tag}_sin_reason:{single_reason_tag} ({relay_act_info}) 故障设备[{dev_name}:{dev_id}]"
                    print(key)
                    # print(f"event_id:{event_id} {key} num:{f['fault_num']} level:{ev_info['fault_level']} st:{} off:{len(off_vec)} risk:{len(risk_vec)} over:{len(over_vec)} stop:{stop} over:{over} over_r:{over_reason} single:{single} single_reason:{single_reason}")
