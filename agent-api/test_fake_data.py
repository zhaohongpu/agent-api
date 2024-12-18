import requests
import json
from third.zheda.parser import get_plan_nn_info, get_plan_n1_info, get_plan_single_info

if __name__ == '__main__':

    fault_desc = {
        "type": "fault_desc",
        "data": {
            "images": {
                "gongqu_url": "http://28.44.2.46:8080/GAS/WebPage/business/gas/bigModelChain/dzGraph.html?eventId=6605",
                "user_url": "http://28.44.2.46:8080/GAS/WebPage/business/gas/bigModelChain/vipUser.html?eventId=6605"
            }
        }
    }

    with open('demo/plan_nn.json', 'r') as f:
        json_str = f.read()
        data = json.loads(json_str)
        info = get_plan_nn_info(data['data'])

        result = {
            "type": "plan",
            "data": {
                "plan_type": "n_n",
                "plan_info": info,
                "images": {
                    "url1": "http://statics-nrxt.dcloud.sh.dc.sgcc.com.cn:1082/GAS/WebPage/business/gas/bigModelChain/subBusConn.html",
                    "url2": "http://statics-nrxt.dcloud.sh.dc.sgcc.com.cn:1082/GAS/WebPage/business/gas/bigModelChain/subBusConn.html",
                    "url3": "http://statics-nrxt.dcloud.sh.dc.sgcc.com.cn:1082/GAS/WebPage/business/gas/bigModelChain/subBusConn.html",
                }
            }
        }

        result = json.dumps(result, ensure_ascii=False)
        print(result)

    with open('demo/plan_n1.json', 'r') as f:
        json_str = f.read()
        # print(type(json_str))
        plan = json.loads(json_str)

        plan['data']['subName'] = '医高站'

        info = get_plan_n1_info(plan['data'])
        # info = get_plan_single_info(plan['data'])

        result = {
            "type": "plan",
            "data": {
                "plan_type": "single",
                "plan_info": info,
                "images": {
                    "url1": "http://statics-nrxt.dcloud.sh.dc.sgcc.com.cn:1082/GAS/WebPage/business/gas/bigModelChain/subBusConn.html",
                    "url2": "http://statics-nrxt.dcloud.sh.dc.sgcc.com.cn:1082/GAS/WebPage/business/gas/bigModelChain/subBusConn.html",
                    "url3": "http://statics-nrxt.dcloud.sh.dc.sgcc.com.cn:1082/GAS/WebPage/business/gas/bigModelChain/subBusConn.html",
                }
            }
        }

        result = json.dumps(result, ensure_ascii=False)
        # print(result)


    with open('demo/ticket_nn.json', 'r') as f:
        json_str = f.read()
        data = json.loads(json_str)

        id = data["content"]["czpid"]

        result = {
            "type": "ticket",
            "data": {
                "ticket_type": "n_n",
                "ticket_info": data["content"],
                "image": "http://31.0.2.107:8000/netorder/otherPage/gis.jsp?ticketId="+ id
            }
        }

        result = json.dumps(result, ensure_ascii=False)
        # print(result)
