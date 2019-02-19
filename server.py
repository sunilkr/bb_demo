import threading
import SocketServer 
import json
import logging
import time

from led import LED, LED_NAMES

tcp_stop_event = threading.Event()
udp_stop_event = threading.Event()

class TCPRequestHandler(SocketServer.BaseRequestHandler):
    def setup(self):
        self.logger = logging.getLogger(str(self.__class__))
        
    def handle(self):
        req_raw = self.request.recv(1024)
        self.logger.debug("Recv from:{0}, data:{1}".format(self.client_address, req_raw))
        try:
            req = json.loads(req_raw)
        except Exception:
            self.logger.exception("Failed to parse request: {0}".format(req_raw))
            socket.sendto(json.dumps({"code":-1, "data":"Error"}), self.client_address)
            return

        if req['cmd'] == 'led-control':
            data = req['data']
            led = LED(LED_NAMES.get(data['led-name'].upper()))
            if data['op'].lower() == 'blink':
                if led.blink(count=data.get('count',1), delay=data.get('delay', 0.5)):
                    self.request.sendall(json.dumps({"code":0, "data":"OK"}))
                else:
                    self.request.sendall(json.dumps({"code":1, "data":"FAIL"}))
        elif req['cmd'] == 'quit':
                tcp_stop_event.set()
                self.request.sendall(json.dumps({"code":1, "data":"OK"}))
        self.logger.debug("Request handled.")


class UDPRequestHandler(SocketServer.BaseRequestHandler):

    def setup(self):
        self.logger = logging.getLogger(str(self.__class__))    

    def handle(self):
        req_raw = self.request[0].strip()
        socket = self.request[1]
        self.logger.debug("Recv from:{0}, data:{1}".format(self.client_address, req_raw))
        try:
            req = json.loads(req_raw)
        except Exception:
            self.logger.exception("Failed to parse request: {0}".format(req_raw))
            socket.sendto(json.dumps({"code":-1, "data":"Error"}), self.client_address)
            return
        
        if req['cmd'] == 'led-control':
            data = req['data']
            led = LED(LED_NAMES.get(data['led-name'].upper()))
            if data['op'].lower() == 'blink':
                if led.blink(count=data.get('count',1), delay=data.get('delay', 0.5)):
                    socket.sendto(json.dumps({"code":0, "data":"OK"}), self.client_address)
                else:
                    socket.sendto(json.dumps({"code":1, "data":"FAIL"}), self.client_address)
        elif req['cmd'] == 'quit':
                udp_stop_event.set()
                socket.sendto(json.dumps({"code":0, "data":"OK"}), self.client_address)
        self.logger.debug("Request handled.")


class Server(object):
    class TCPThreaded(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
        pass

    class UDPThreaded(SocketServer.ThreadingMixIn, SocketServer.UDPServer):
        pass

    config = None
    tcp_server = None
    udp_server = None

    @classmethod
    def start_all(cls, config):
        cls.logger = logging.getLogger(str(cls))
        
        cls.logger.info("Loading config from {0}".format(config))
        with open(config, "r") as cfg:
            cls.config = json.load(cfg)
        host = cls.config['server']['ip']
        tcp_port = cls.config['server']['port']['tcp']
        udp_port = cls.config['server']['port']['udp']
        
        cls.logger.info("Creating threaded TCP server on {0}".format((host, tcp_port)))
        cls.tcps = cls.TCPThreaded((host, tcp_port), TCPRequestHandler)
        cls.logger.info("Creating threaded UDP server on {0}".format((host, udp_port)))
        cls.udps = cls.UDPThreaded((host, udp_port), UDPRequestHandler)
        
        cls.logger.info("Creating server threads...")
        thread_tcp = threading.Thread(target=cls.tcps.serve_forever)
        thread_udp = threading.Thread(target=cls.udps.serve_forever)
        thread_tcp.daemon = True
        thread_udp.daemon = True
        
        cls.logger.info("Starting server threads...")
        thread_tcp.start()
        tcps_running = True
        thread_udp.start()
        udps_running = True
        
        cls.logger.info("Waiting for stop events...")
        while True:
            if tcp_stop_event.is_set() and tcps_running:
                cls.logger.info("Shutting down TCP server...")
                cls.tcps.shutdown()
                cls.tcps.server_close()
                tcps_running = False

            if udp_stop_event.is_set() and udps_running:
                cls.logger.info("Shutting down UDP server...")
                cls.udps.shutdown()
                cls.udps.server_close()
                udps_running = False
            
            if (tcp_stop_event.is_set() and udp_stop_event.is_set()):
                break
            else:
                tcp_stop_event.wait(0.5)
                udp_stop_event.wait(0.5)

        thread_tcp.join()
        thread_udp.join()
        cls.logger.info("All servers shutdown.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    Server.start_all("config.json")