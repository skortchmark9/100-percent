import time
import memcache
mc = memcache.Client(['127.0.0.1:11211'], debug=0)
counter = 0

while True:
    time.sleep(3)
    key = 'chunk' + str(counter)
    result = mc.get(key)
    print(key, result)
    if result:
        counter += 1