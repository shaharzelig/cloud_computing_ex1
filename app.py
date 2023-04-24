#!flask/bin/python
from flask import Flask, jsonify, abort, make_response, request

app = Flask(__name__)
@app.route('/entry', methods=['POST'])
def get_tasks():
    plate = request.args.get('plate')
    parking_lot = request.args.get('parkingLot')

    return jsonify({'plate': plate, 'parkingLot': parking_lot})
@app.route('/exit', methods=['POST'])
def exit(task_id):
    ticket_id = request.args.get('ticketId')
    return jsonify({'ticketId': ticket_id})


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=443)