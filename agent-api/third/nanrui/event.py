from kafka import KafkaConsumer, KafkaProducer
import json
import os
import datetime
from third.nanrui import isw_cloud_data_pb2
from third.nanrui.parser import pb2dict
from common import get_path, set_consumer_log


def run_produce():
    bootstrap_servers = os.getenv("KAFKA_SERVERS", "172.20.10.3:9092")
    # bootstrap_servers = "10.130.16.112:9092,10.130.16.120:9092,10.130.16.121:9092"
    topic = os.getenv("KAFKA_TOPIC", "isw_cloud_data")

    producer = KafkaProducer(bootstrap_servers=bootstrap_servers)

    # 读取二进制数据
    with open(get_path('/demo/6605.data'), 'rb') as file:
        data = file.read()

    fault_info_list = isw_cloud_data_pb2.isw_fault_info_list()

    fault_info_list.ParseFromString(data)

    str = fault_info_list.SerializeToString()

    producer.send(topic, str)
    print("Sent")

    producer.flush()
    producer.close()


def run_consumer():
    bootstrap_servers = os.getenv("KAFKA_SERVERS", "172.20.10.3:9092")
    # bootstrap_servers = "10.130.16.112:9092,10.130.16.120:9092,10.130.16.121:9092"
    topic = os.getenv("KAFKA_TOPIC", "isw_cloud_data")

    consumer = KafkaConsumer(topic,
                             bootstrap_servers=bootstrap_servers,
                             # group_id='my_group',
                             auto_offset_reset='earliest')
    # auto_offset_reset='latest')  # 默认，从最近开始消费
    # auto_offset_reset='earliest')  # 从最老开始消费
    # 如果提交了offset，则不受以上设置影响

    index = 1
    for message in consumer:
        try:
            fault_info_list = isw_cloud_data_pb2.isw_fault_info_list()
            fault_info_list.ParseFromString(message.value)
            dict = pb2dict(fault_info_list)

            event_id = dict['fault_list'][0]['event_id']
            json_str = json.dumps(dict, ensure_ascii=False)

            with open(get_path('/data/fault_by_event_id/{}.json'.format(event_id)), 'w') as f:
                f.write(json_str)

            with open(get_path('/data/fault_by_event_id/{}.data'.format(event_id)), 'wb') as f:
                f.write(message.value)

            with open(get_path('/data/fault_by_index/{}_{}.json'.format(event_id, index)), 'w') as f:
                f.write(json_str)

            with open(get_path('/data/fault_by_index/{}_{}.data'.format(event_id, index)), 'wb') as f:
                f.write(message.value)

            set_consumer_log("consumer index:%d event_id:%d" % (index, event_id))

            index = index + 1

        except Exception as e:
            index = index + 1
            set_consumer_log("consumer error occurred index: %d" % index)

if __name__ == "__main__":
    with open(get_path('/demo/6605.data'), 'rb') as file:
        data = file.read()

    fault_info_list = isw_cloud_data_pb2.isw_fault_info_list()
    fault_info_list.ParseFromString(data)

    # print(fault_info_list)

    info = pb2dict(fault_info_list)
    print(json.dumps(info, ensure_ascii=False))