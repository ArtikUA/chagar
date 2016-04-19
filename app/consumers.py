import json
import logging
import random
from time import sleep
import math

from channels import Group

logger = logging.getLogger('chat')

coords = {}


def ws_add(data):
    Group('chat').add(data.reply_channel)


def ws_message(json_object):
    data = json.loads(json_object.content['text'])

    uuid = data['uuid']
    action = data['action']

    if action == 'goal':
        logger.debug("goal %s" % data)

        goal(data, uuid)

    if action == 'start':
        logger.debug("start %s" % data)

        start(uuid)


def ws_disconnect(data):
    Group('chat').discard(data.reply_channel)


def start(uuid):
    new_circle(uuid)

    load_circles()

    while True:
        goal_x = coords[uuid]['goal_x']
        goal_y = coords[uuid]['goal_y']

        x = coords[uuid]['x']
        y = coords[uuid]['y']

        move_circle(uuid, x, y, goal_x, goal_y)

        sleep(0.01)


def change_circle(uuid):
    data_send = {
        'action': 'move',
        'uuid': uuid,
        'x': coords[uuid]['x'],
        'y': coords[uuid]['y']
    }
    Group('chat').send({'text': json.dumps(data_send)})
    logger.debug('change_circle %s' % uuid)


def load_circles():
    for key, value in coords.items():
        data_send = {
            'action': 'start',
            'uuid': key,
            'x': value['x'],
            'y': value['y'],
        }
        Group('chat').send({'text': json.dumps(data_send)})


def new_circle(uuid):
    start_x = random.randint(0, 800)
    start_y = random.randint(0, 800)
    start_x = 400
    start_y = 400

    coords[uuid] = {
        'goal_x': start_x,
        'x': start_x,
        'goal_y': start_y,
        'y': start_y,
    }


def move_circle(uuid, a_x, a_y, b_x, b_y):
    changes = False
    v = 1 if b_x > a_x else -1

    if abs(b_x - a_x) > 2 or abs(b_y - a_y) > 2:
        d = math.atan((a_y - b_y) / (a_x - b_x))
        c_x = a_x + v * math.cos(d)
        c_y = a_y + v * math.sin(d)

        coords[uuid]['x'] = c_x
        coords[uuid]['y'] = c_y
        changes = True

    if changes:
        change_circle(uuid)


def goal(data, uuid):
    goal_x = float(data['goal_x'])
    goal_y = float(data['goal_y'])

    coords[uuid]['goal_x'] = goal_x
    coords[uuid]['goal_y'] = goal_y
