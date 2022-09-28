""" Crude Server

This is supplementary code for a tutorial about writing HTTP servers from scratch.

To get a better understanding, read the tutorial at this link: 

https://bhch.github.io/posts/2017/11/writing-an-http-server-from-scratch/

"""

import os
import time
from concurrent.futures import ThreadPoolExecutor
import socket
from client import HTTPServer
from request_parse import HTTPRequest


class TCPServer:
    """Base server class for handling TCP connections. 
    The HTTP server will inherit from this class.
    """

    def __init__(self, host='127.0.0.1', port=8888, max_conn=7):
        super().__init__()
        self.host = host
        self.port = port
        self.max_conn = max_conn
        # build a log once running
        clock = time.localtime()
        self.log_name = "log/" + str(clock.tm_year) + "-" + str(
            clock.tm_mon) + "-" + str(clock.tm_mday) + " " + str(
            clock.tm_hour) + "_" + str(clock.tm_min) + "_" + str(
            clock.tm_sec) + ".txt"

    def start(self):
        """Method for starting the server"""
        # create socket object
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # bind the socket object to the address and port
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        server_socket.settimeout(60)

        # 线程池
        thread_pool = ThreadPoolExecutor(self.max_conn)

        print("Listening at", server_socket.getsockname())

        while True:
            try:
                # accept any new connection
                client_conn, client_addr = server_socket.accept()
                print("Connected by", client_addr)
            except socket.timeout:
                print("Main server timeout!")
                continue
            except KeyboardInterrupt:
                break
            thread_pool.submit(HTTPServer(server_socket, client_conn, client_addr, self.log_name))

        thread_pool.shutdown(wait=True)


class Client:
    def __init__(self, socket, conn, addr, log_name):
        self.socket = socket
        self.conn = conn
        self.addr = addr
        self.log_name = log_name
        # self.setDaemon(True)
        # self.start()

    def __call__(self, *args, **kwds):
        return self.run()

    def run(self):
        # read the data sent by the client
        # reading just the first 1024 bytes sent by the client.
        data = self.conn.recv(1024)
        response = self.handle_request(data)
        # send back the data to client
        self.conn.sendall(response)
        # close the connection
        self.conn.close()

    def handle_request(self, data):
        """Handles incoming data and returns a response.
        Override this in subclass.
        """
        return data


if __name__ == '__main__':
    server = TCPServer()
    server.start()
