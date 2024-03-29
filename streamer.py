import nsq
import ujson
import memcache
import re

pattern = re.compile(r'^htt[ps]+:\/\/www\.nytimes.com\/[\d][\d][\d][\d]\/[\d][\d]\/[\d][\d]\/.+\.html')

class Streamer(nsq.Reader):
    """Chunks 4 Jake"""
    def __init__(self):
        super(Streamer, self).__init__(
            message_handler=self.handler,
            nsqd_tcp_addresses=['bigwheel.nytlabs.com:8888'],
            topic='event_tracker-page', channel='jake.soloff#ephemeral', lookupd_poll_interval=15, max_in_flight=500)
        self.chunk = []
        self.mc = memcache.Client(['127.0.0.1:11211'], debug=0)
        self.MAX_CHUNK_SIZE = 20
        self.CURRENT_CHUNK_SIZE = 0
        nsq.run()

    def save_chunk(self):
        num_chunks = self.mc.get('num_chunks') or 0
        key = 'chunk' + str(num_chunks)
        print(key)
        self.mc.set(key, self.chunk)
        self.mc.incr('num_chunks')
        self.chunk = []
        self.CURRENT_CHUNK_SIZE = 0

    def handler(self, message):
        data = ujson.loads(message.body)
        url = data['url']
        match = re.search(pattern, url)
        if not match:
            return True

        user = data['regi']

        if url and user:
            self.chunk.append((url, user))
            self.CURRENT_CHUNK_SIZE += 1

        if (self.CURRENT_CHUNK_SIZE == self.MAX_CHUNK_SIZE):
            self.save_chunk()

        return True