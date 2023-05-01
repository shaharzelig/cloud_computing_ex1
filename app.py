#!flask/bin/python
import time

from flask import Flask, jsonify, abort, request
import random
app = Flask(__name__)

# No data persistence for now :)
DB = {}


@app.route('/entry', methods=['POST'])
def entry():
    plate = request.args.get('plate')
    parking_lot = request.args.get('parkingLot')
    if not plate or not parking_lot:
        abort(400, "Missing plate or parkingLot parameter")

    ticket_id = str(random.randint(0, 10000)).zfill(5)
    while ticket_id in DB.keys():
        ticket_id = str(random.randint(0, 10000)).zfill(5)

    DB[ticket_id] = {'plate': plate, 'parkingLot': parking_lot, "time": int(time.time())}
    return ticket_id


@app.route('/exit', methods=['POST'])
def parking_exit():
    ticket_id = request.args.get('ticketId')
    if ticket_id not in DB.keys():
        abort(400, "Invalid ticketId parameter")

    db_entry = DB[ticket_id]
    total_time_in_minutes = (int(time.time()) - db_entry['time']) / 60
    total_amount_of_15_minutes = total_time_in_minutes / 15
    charge = total_amount_of_15_minutes * 2.5   # 2.5 USD for 15 minutes == 10 USD per hour
    return jsonify({"parkingLot": entry['parkingLot'], "plate": entry['plate'], "charge": charge})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
