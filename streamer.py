import nsq
import ujson
import papi
import memcache

class Streamer(nsq.Reader):
    """Chunks 4 Jake"""
    def __init__(self):
        super(Streamer, self).__init__(
            message_handler=self.handler,
            nsqd_tcp_addresses=['bigwheel.nytlabs.com:8888'],
            topic='event_tracker-page', channel='samuel.kortchmar#ephemeral', lookupd_poll_interval=15)
        self.chunk = []
        self.p = papi.Papi()
        self.mc = memcache.Client(['127.0.0.1:11211'], debug=0)
        self.MAX_CHUNK_SIZE = 20
        self.chunks = 0
        self.CURRENT_CHUNK_SIZE = 0
        nsq.run()

    def save_chunk(self):
        print('chunk' + str(self.chunk))
        self.mc.set('chunk' + str(self.chunks), self.chunk)
        self.chunk = []
        self.CURRENT_CHUNK_SIZE = 0
        self.chunks += 1

    def handler(self, message):
        data = ujson.loads(message.body)
        url = data['url']
        user = data['regi']

        if url and user and self.p.get_url(url):
            print('chunking')
            self.chunk.append((url, user))
            self.CURRENT_CHUNK_SIZE += 1

        if (self.CURRENT_CHUNK_SIZE == self.MAX_CHUNK_SIZE):
            print('saving')
            self.save_chunk()


        return True