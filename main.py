import tornado.ioloop
import tornado.web
import tornado.websocket
import logging
import traceback

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s - %(levelname)s - %(message)s")
port = 8888
server_peer = dict()
client_peer = dict()
server_connect_id = 0
client_connect_id = 0


class serverWebSocket(tornado.websocket.WebSocketHandler):

    def check_origin(self, origin):
        return True

    def open(self):
        global server_connect_id, server_peer
        logging.info("server connect opened,id is:%s", server_connect_id)
        server_peer[str(server_connect_id)] = self
        self.connect_id = server_connect_id
        server_connect_id += 1

    def on_message(self, message):
        global client_peer
        logging.info("get server msg:%s", message)
        try:
            for (k, peer) in client_peer.items():
                peer.write_message(message)
        except Exception as identifier:
            logging.error(identifier)

    def on_close(self):
        global server_peer
        server_peer.pop(str(self.connect_id))
        logging.info("server connect closed")


class ClientWebSocket(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        global client_connect_id, client_peer
        logging.info("client connect opened,id is:%s", client_connect_id)
        client_peer[str(client_connect_id)] = self
        self.connect_id = client_connect_id
        client_connect_id += 1

    def on_message(self, message):
        global server_peer
        logging.info("get client msg:%s", message)
        try:
            logging.info(server_peer)
            for (k, peer) in server_peer.items():
                logging.info(peer)
                peer.write_message(message)
        except Exception as identifier:
            logging.error(identifier)

    def on_close(self):
        global client_peer
        client_peer.pop(str(self.connect_id))
        logging.info("client connect closed")


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        global server_peer
        self.write("server connect count:" + str(len(server_peer)))


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/server", serverWebSocket),
        (r"/client", ClientWebSocket),

    ], debug=True)


if __name__ == "__main__":
    logging.info("ws server start at : %s ", port)
    app = make_app()
    app.listen(port)
    tornado.ioloop.IOLoop.current().start()
