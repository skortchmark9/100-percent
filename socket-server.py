from tornado import websocket
import tornado.ioloop
import tornado.web
import json

class EchoWebSocket(websocket.WebSocketHandler):
    def open(self):
        print("WebSocket opened")

    def on_message(self, message):
        json_data=open('miserables.json').read()
        self.write_message(json_data)

    def on_close(self):
        print("WebSocket closed")

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

if __name__ == "__main__":
    application = tornado.web.Application([
        (r"/", MainHandler),
        (r'/websocket', EchoWebSocket)
    ])
    application.listen(8081)
    tornado.ioloop.IOLoop.current().start()