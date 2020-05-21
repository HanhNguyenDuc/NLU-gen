from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import requests
import logging
import sys
import argparse
import os
import json
import random
import glob
import re
import dotenv
dotenv.load_dotenv()


logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv('SECRET_KEY')
socketio = SocketIO(app)
stories_list = []

parser = argparse.ArgumentParser()
parser.add_argument("--ps", type=int, help="Port of Server running", default = 6999)

args = parser.parse_args()
stories_generator = None

messages_dict = dict()

def backtrack(slots_list, slots_values, i, res, id=0):
    '''
        slots_list: list of slots
        slots_values: dictionary which each key contain possible values
        i: iterator
        res: result of the previous loop
    '''
    global messages_dict
    messages_list = messages_dict.get(id)
    # print(intent_text)
    slot_name = slots_list[i]
    values = slots_values[slot_name]
    # print(intents)
    for value in values:
        current_result = (res + '.')[:-1]
        current_result = current_result.replace('{' + slot_name + '}', value)
        if i == len(slots_list) - 1:
            # print(current_result)
            messages_list.append(current_result)
        else:
            backtrack(slots_list, slots_values, i+1, current_result, id)


@app.route('/')
def index():
    return render_template('index.html')

@socketio.on("send_template")
def process_template(json_data):
    # json_data = json.loads(json_data)
    id = json_data.get('id')
    message = json_data.get('message')
    slot_list = re.findall('\{(.*?)\}', message)
    slot_list = list(set(slot_list))
    response = {
        'slot_list': slot_list
    }
    socketio.emit("get_slot", {
        "slot_list": slot_list,
        "id": id
    })

@socketio.on("send_slots")
def process_slots(json_data):
    # we generate data here
    global messages_dict
    id = json_data.get('id')
    messages_dict[str(id)] = []
    slots = json_data.get('slots')
    message = json_data.get('message')
    slots_values = {}
    slots_list = []
    for key in slots:
        slots_list.append(key)
        slot_arr = slots.get(key).split(',')
        slots_values.update({key: slot_arr})
    backtrack(slots_list, slots_values, 0, message, id=str(id))
    logging.debug('{}'.format(id))
    socketio.emit("show_data", {
        "message_list": messages_dict[str(id)],
        "id": id
    })
    del messages_dict[str(id)]


if __name__ == '__main__':
	socketio.run(app, port=6969, host = os.getenv('HOST') ,debug = True)


