import json
import logging
from time import sleep

import redis
from channels import Group

logger = logging.getLogger('chat')

r = redis.StrictRedis(host='localhost', port=6379, db=5)
r.flushdb()


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


def move_y(changes, goal_y, uuid, y):
    if abs(goal_y - y) > 2:
        next_y = y
        if goal_y > y:
            next_y = y + 1
        elif goal_y < y:
            next_y = y - 1

        r.set('%s:y' % uuid, next_y)
        changes = True
    return changes


def move_x(changes, goal_x, uuid, x):
    if abs(goal_x - x) > 2:
        next_x = x
        if goal_x > x:
            next_x = x + 1
        elif goal_x < x:
            next_x = x - 1

        r.set('%s:x' % uuid, next_x)
        changes = True
    return changes


def start(uuid):
    r.set('%s:goal_x' % uuid, 100)
    r.set('%s:x' % uuid, 100)
    r.set('%s:goal_y' % uuid, 100)
    r.set('%s:y' % uuid, 100)

    # r.hset(uuid, 'goal_x', 100)
    # r.hset(uuid, 'x', 100)
    # r.hset(uuid, 'goal_y', 100)
    # r.hset(uuid, 'y', 100)

    initial_hash = {
        'goal_x': 100,
        'x': 100,
        'goal_y': 100,
        'y': 100
    }
    r.hmset(uuid, initial_hash)

    for key in r.keys('*'):
        if len(key) == 36:
            hmap = r.hgetall(key)

            data_send = {
                'action': 'start',
                'uuid': key.decode('utf8'),
                'x': int(hmap[b'x']),
                'y': int(hmap[b'y'])
            }
            Group('chat').send({'text': json.dumps(data_send)})

    while True:

        goal_x = float(r.get('%s:goal_x' % uuid))
        goal_y = float(r.get('%s:goal_y' % uuid))

        x = float(r.get('%s:x' % uuid))
        y = float(r.get('%s:y' % uuid))

        changes = False

        if not x:
            r.set('%s:x' % uuid, goal_x)
        else:
            changes = move_x(changes, goal_x, uuid, x)
            changes = move_y(changes, goal_y, uuid, y)

        if changes:
            data_send = {
                'action': 'move',
                'uuid': uuid,
                'x': x,
                'y': y
            }

            Group('chat').send({'text': json.dumps(data_send)})

            logger.debug('frame %s' % uuid)
        sleep(0.01)


def goal(data, uuid):
    goal_x = float(data['goal_x'])
    goal_y = float(data['goal_y'])
    r.set('%s:goal_x' % uuid, goal_x)
    r.set('%s:goal_y' % uuid, goal_y)
