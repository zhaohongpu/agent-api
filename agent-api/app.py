import os
import multiprocessing
import time

from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room
import sys
from common import set_consumer_log, is_mock_conversation_id, logger, get_file, get_conversation_id, to_json
from api.fault_desc import fault_desc_api
from api.fault_analysis import fault_analysis_api
from api.create_plan import create_plan_api
from api.create_plan_n1 import create_plan_n1_api
from api.create_plan_single import create_plan_single_api
from api.create_ticket import create_ticket_api
from api.exec_ticket import exec_ticket_api
from api.create_plan_nn_v2 import create_plan_nn_v2_api
from api.create_plan_n1_v2 import create_plan_n1_v2_api
from api.optimize_plan_nn_v2 import optimize_plan_nn_v2_api

from third.nanrui.event import run_consumer

os.environ['TZ'] = 'Asia/Shanghai'
time.tzset()

root_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(root_path)
app = Flask(__name__, static_folder="static")
app.config.from_object(__name__)
app.config["JSON_AS_ASCII"] = False

socketio = SocketIO(app, cors_allowed_origins="*")


@app.route('/agent/api')
def hello_world():
    logger.debug("hello_{}".format('world'))
    socketio.emit('message', '{"type":"debug","data":"hello"}', room='default')
    return 'Hello, World!'


@app.route('/agent/api/post_message', methods=['POST'])
def post_message():
    conversation_id = get_conversation_id(request)
    message = request.form.get('message', '')
    logger.info(f"post_message conv_id[{conversation_id}] message[{message}]")
    if conversation_id and message:
        data = {
            'type': 'chat',
            'data': message
        }
        socketio.emit('message', to_json(data), room=conversation_id)
        return 'OK'
    else:
        return 'FAIL'


@app.route('/agent/api/app.log')
def app_log():
    return get_file('/log/app.log').replace('\n', '<br>')


@app.route('/agent/api/app.log.wf')
def app_log_wf():
    return get_file('/log/app.log.wf').replace('\n', '<br>')


@socketio.on('connect')
def handle_connect():
    client_sid = request.sid
    logger.info(f"websocket client connected with session ID:{client_sid}")


@socketio.on('join_room')
def handle_join_room(data):
    conversation_id = data.get('room')
    if is_mock_conversation_id():
        conversation_id = 'default'

    join_room(conversation_id)
    message = 'handle_join_room, you have joined room conversation_id:%s' % conversation_id
    logger.info(message)
    emit('message', '{"type":"debug","data":"' + message + '"}', room=conversation_id)


# 故障描述
@app.route('/agent/api/fault_desc', methods=['POST'])
def fault_desc():
    return fault_desc_api(request, socketio, app)


# 故障分析
@app.route('/agent/api/fault_analysis', methods=['POST'])
def fault_analysis():
    return fault_analysis_api(request, socketio, app)


# 全停转供方案生成
@app.route('/agent/api/create_plan', methods=['POST'])
def create_plan():
    return create_plan_api(request, socketio, app)


# N-1转供方案生成
@app.route('/agent/api/create_plan_n1', methods=['POST'])
def create_plan_n1():
    return create_plan_n1_api(request, socketio, app)


# 单电源方案生成
@app.route('/agent/api/create_plan_single', methods=['POST'])
def create_plan_single():
    return create_plan_single_api(request, socketio, app)


# 操作票生成
@app.route('/agent/api/create_ticket', methods=['POST'])
def create_ticket():
    return create_ticket_api(request, socketio, app)


# 操作票下发执行
@app.route('/agent/api/exec_ticket', methods=['POST'])
def exec_ticket():
    return exec_ticket_api(request, socketio, app)

@app.route('/agent/api/create_plan_nn_v2', methods=['POST'])
def create_plan_nn_v2():
    return create_plan_nn_v2_api(request, socketio, app)


@app.route('/agent/api/optimize_plan_nn_v2', methods=['POST'])
def optimize_plan_nn_v2():
    return optimize_plan_nn_v2_api(request, socketio, app)


@app.route('/agent/api/create_plan_n1_v2', methods=['POST'])
def create_plan_n1_v2():
    return create_plan_n1_v2_api(request, socketio, app)


def consumer_worker():
    set_consumer_log("consumer worker process ID: %d" % (os.getpid()))
    run_consumer()


if __name__ == "__main__":
    if os.getenv('KAFKA_CONSUMER_ENABLE') == '1':
        # 开一个守护进程用于kafka数据消费
        p = multiprocessing.Process(target=consumer_worker)
        p.daemon = True  # 守护进程
        p.start()

    APP_DEBUG_ENABLE = os.getenv('APP_DEBUG_ENABLE', '0') == '1'

    port = os.getenv('APP_PORT', 8188)
    socketio.run(app, host='0.0.0.0', port=port, debug=APP_DEBUG_ENABLE, allow_unsafe_werkzeug=True)
