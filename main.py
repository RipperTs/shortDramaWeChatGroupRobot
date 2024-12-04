from flask import Flask, request, jsonify

from scheduled.topic_task import TopicTaskScheduled
from service.messages_service import MessageService

app = Flask(__name__)
wxbot_service = MessageService()


@app.route('/')
def index():
    return 'Hello World!'


@app.route('/api/robot-msg', methods=['POST', 'GET'])
def handle_post():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    try:
        wxbot_service.get_messages(data)
        return jsonify({'msg': 'ok'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # 初始化定时任务
    TopicTaskScheduled.init_tasks()
    # 启动服务
    app.run(debug=False, host='0.0.0.0', port=12300)
