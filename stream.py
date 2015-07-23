import nsq
import ujson
import papi

def handler(message):
    url = ujson.loads(message.body)['url']

    print(p.get_url(url))

    return True

p = papi.Papi()
r = nsq.Reader(message_handler=handler,
        nsqd_tcp_addresses=['bigwheel.nytlabs.com:8888'],
        topic='event_tracker-page', channel='samuel.kortchmar#ephemeral', lookupd_poll_interval=15)
nsq.run()