#!flask/bin/python
import time

from flask import Flask, jsonify, abort, make_response, request
import random
app = Flask(__name__)

# No data persistence for now
DB = {}

@app.route('/entry', methods=['POST'])
def entry():
    plate = request.args.get('plate')
    parking_lot = request.args.get('parkingLot')
    ticket_id = str(random.randint(0, 10000)).zfill(5)
    while ticket_id in DB.keys():
        ticket_id = str(random.randint(0, 10000)).zfill(5)

    DB[ticket_id] = {'plate': plate, 'parkingLot': parking_lot, "time": int(time.time())}
    return ticket_id

@app.route('/exit', methods=['POST'])
def exit():
    ticket_id = request.args.get('ticketId')
    if ticket_id not in DB.keys():
        abort(404)

    entry = DB[ticket_id]
    total_time_in_minutes = (int(time.time()) - entry['time']) / 60
    total_amount_of_15_minutes = total_time_in_minutes / 15
    charge = total_amount_of_15_minutes * 2.5 # 2.5 USD for 15 minutes == 10 USD per hour
    return jsonify({"parkingLot": entry['parkingLot'], "plate": entry['plate'], "charge": charge})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)