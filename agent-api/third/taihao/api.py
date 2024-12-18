import requests
import json
from common import get_path, set_cache, is_mock_third_api, get_file


def create_ticket(plan_json_str, type=""):
    url = "http://10.130.16.61:8091/czpServices/CzpService/getTicketInfo"

    headers = {
        'Content-Type': 'application/json'
    }

    if isinstance(plan_json_str, dict):
        plan_json_str = json.dumps(plan_json_str, ensure_ascii=False)

    set_cache("api_create_ticket_%s_input" % type, plan_json_str)

    if is_mock_third_api():
        result = get_file('/demo/ticket_nn.json', return_json=True)
        return result

    response = requests.post(url, plan_json_str, headers=headers)
    response = json.loads(response.content)
    set_cache("api_create_ticket_%s_output" % type, response)
    return response


def get_ticket_status(ticket_id):
    url = "http://10.130.16.61:8088/netorder/CzpInteract/getCzpInfo"

    headers = {
        'Content-Type': 'application/json'
    }

    data = {
        "interfaceCode": "",
        "paramType": "json",
        "param": {
            "data": [
                {
                    "obj_id": ticket_id
                }
            ]
        }
    }

    response = requests.post(url, data=json.dumps(data), headers=headers)
    response = json.loads(response.content)
    return response


if __name__ == "__main__":
    with open(get_path('/demo/plan_nn.json'), 'r') as file:
        data = file.read()
        data = json.loads(data)

    response = create_ticket(data['data'], type="nn")
    print(response)

    ticket_id = response['content']['czpid']

    response = get_ticket_status(ticket_id)
    print(response)


