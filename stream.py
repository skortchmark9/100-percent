import nsq
import json
import papi

def handler(message):
    papi.get_tags(json.loads(message.body)['url'])
    return True

r = nsq.Reader(message_handler=handler,
        nsqd_tcp_addresses=['bigwheel.nytlabs.com:8888'],
        topic='event_tracker-page', channel='samuel.kortchmar#ephemeral', lookupd_poll_interval=15)
nsq.run()