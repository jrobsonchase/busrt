import elbus
import time
from argparse import ArgumentParser

ap = ArgumentParser()
ap.add_argument('NAME')
ap.add_argument('TARGET')
ap.add_argument('MESSAGE')

a = ap.parse_args()

# def on_message(message):
# print(message.type, message.sender, message.topic, message.payload)

name = a.NAME
target = a.TARGET
bus = elbus.client.Client('/tmp/elbus.sock', name)
# bus = elbus.client.Client('localhost:9924', name)
rpc = elbus.rpc.Rpc(bus)
# bus.on_message = on_message
bus.connect()
payload = a.MESSAGE
if payload.startswith(":"):
    request_id = 1
    if ':' in payload[1:]:
        method, params = payload[1:].split(':', maxsplit=1)
    else:
        method = payload[1:]
        params = ''
    request = elbus.rpc.Request(method, params)
    result = rpc.call(target, request).wait_completed().get_payload()
    try:
        import msgpack, json
        data = msgpack.loads(result, raw=False, strict_map_key=False)
        print(json.dumps(data))
    except:
        print(result)
elif payload.startswith('.'):
    notification = elbus.rpc.Notification(payload[1:])
    print(hex(rpc.notify(target, notification).wait_completed()))
else:
    m = elbus.client.Frame(payload)
    if target.startswith('='):
        target = target[1:]
        m.type = elbus.client.OP_PUBLISH
    elif '*' in target or '?' in target:
        m.type = elbus.client.OP_BROADCAST
    print(hex(bus.send(target, m).wait_completed()))
    bus.disconnect()
