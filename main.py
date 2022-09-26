""" Crude Server

This is supplementary code for a tutorial about writing HTTP servers from scratch.

To get a better understanding, read the tutorial at this link: 

https://bhch.github.io/posts/2017/11/writing-an-http-server-from-scratch/

"""

import os
import time
from concurrent.futures import ThreadPoolExecutor
import subprocess
import socket
import mimetypes
import threading


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


class HTTPServer(Client):
    """The actual client class."""

    # log's messages
    log_lines = ""
    log_headers = ""
    log_body = ""
    log_status = 0
    request = None

    # server's name and the type of return
    headers = {
        'Server': 'BIT-Server',
        'Content-Type': 'text/html',
    }

    status_codes = {
        200: 'OK',
        404: 'Not Found',
        403: 'Forbidden',
        501: 'Not Implemented',
    }

    def handle_request(self, data):
        """Handles incoming requests"""

        self.request = HTTPRequest(data)  # Get a parsed HTTP request

        try:
            # Call the corresponding handler method for the current 
            # request's method
            handler = getattr(self, 'handle_%s' % self.request.method)
        except AttributeError:
            handler = self.HTTP_501_handler

        response = handler(self.request)

        return response  # send bytes, not string

    def response_line(self, status_code):
        """Returns response line (as bytes)"""
        reason = self.status_codes[status_code]
        response_lines = 'HTTP/1.1 %s %s\r\n' % (status_code, reason)
        self.log_lines = response_lines

        return response_lines.encode()  # convert from str to bytes

    def response_headers(self, extra_headers=None):
        """Returns headers (as bytes).

        The `extra_headers` can be a dict for sending 
        extra headers with the current response
        """
        headers_copy = self.headers.copy()  # make a local copy of headers

        if extra_headers:
            # update Content-Type
            # 参数：此方法将字典或 键/值对(通常为元组) 的可迭代对象作为参数
            # 返回：它不返回任何值，而是使用字典对象或键/值对的可迭代对象中的元素更新字典
            headers_copy.update(extra_headers)

        headers = ""

        for h in headers_copy:
            headers += '%s: %s\r\n' % (h, headers_copy[h])
        self.log_headers = headers

        return headers.encode()  # convert str to bytes

    def handle_OPTIONS(self, request):
        """Handler for OPTIONS HTTP method"""
        self.log_status = 200
        response_line = self.response_line(200)

        extra_headers = {'Allow': 'OPTIONS, GET'}
        response_headers = self.response_headers(extra_headers)

        blank_line = b'\r\n'

        return b''.join([response_line, response_headers, blank_line])

    def handle_GET(self, request):
        """Handler for GET HTTP method"""

        path = request.uri.strip('/')  # remove slash from URI

        if not path:
            # If path is empty, that means user is at the homepage
            # so just serve index.html
            path = 'index.html'

        if os.path.exists(path) and not os.path.isdir(path):  # don't serve directories
            self.log_status = 200
            response_line = self.response_line(status_code=200)

            # find out a file's MIME type
            # if nothing is found, just send `text/html`
            content_type = mimetypes.guess_type(path)[0] or 'text/html'
            extra_headers = {'Content-Type': content_type}
            response_headers = self.response_headers(extra_headers)
            file_size = os.path.getsize(path)

            with open(path, 'rb') as f:
                response_body = f.read()
        else:
            self.log_status = 404
            response_line = self.response_line(404)
            response_headers = self.response_headers()
            response_body = b'<h1>404 Not Found</h1>'
            file_size = 0

        blank_line = b'\r\n'
        self.log_body = response_body

        # a valid http response
        response = b''.join([response_line, response_headers, blank_line, response_body])

        # TODO: write log
        self.write_log(file_size)

        return response

    def handle_POST(self, request):
        """Handler for POST HTTP method"""

        path = request.uri.strip('/')  # remove slash from URI
        command = 'python ' + path + ' "' + str(request.message) + '" "' + str(self.socket.getsockname()[0]) \
                  + '" "' + str(self.socket.getsockname()[1]) + '"'
        # 用subprocess这个模块来产生子进程,并连接到子进程的标准输入/输出/错误中去，还可以得到子进程的返回值
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        process.wait()

        if process.poll() == 2:  # 文件不存在时返回值为2
            self.log_status = 403
            response_line = self.response_line(403)
            response_headers = self.response_headers()
            response_body = b'<h1>404 Not Found</h1>'
        else:
            self.log_status = 200
            response_line = self.response_line(status_code=200)
            response_headers = self.response_headers()
            response_body = process.stdout.read()

        blank_line = b'\r\n'
        self.log_body = response_body

        # a valid http response
        response = b''.join([response_line, response_headers, blank_line, response_body])
        process.kill()

        # TODO: write log
        file_size = os.path.getsize(path)
        self.write_log(file_size)

        return response

    def HTTP_501_handler(self, request):
        """Returns 501 HTTP response if the requested method hasn't been implemented."""
        self.log_status = 501
        response_line = self.response_line(status_code=501)

        response_headers = self.response_headers()

        blank_line = b'\r\n'

        response_body = b'<h1>501 Not Implemented</h1>'
        self.log_body = response_body

        # TODO: write log
        self.write_log(file_size=0)

        return b"".join([response_line, response_headers, blank_line, response_body])

    def write_log(self, file_size):
        messages = self.request.contents
        # Host and ports
        content = str(self.socket.getsockname()[0]) + " " + str(self.socket.getsockname()[1])
        # time
        content += "--" + "[" + str(time.localtime().tm_mday) + "/" + str(
            time.localtime().tm_mon) + "/" + str(
            time.localtime().tm_year) + "-" + str(
            time.localtime().tm_hour) + ":" + str(
            time.localtime().tm_min) + ":" + str(
            time.localtime().tm_sec) + "] "
        # Get or post method
        content += self.request.method + " "
        # uri
        content += self.request.uri + " "
        # http version
        content += self.request.http_version + " "
        # file size
        content = content + str(file_size) + " "
        content = content + str(self.log_status) + " "

        for line in messages:
            # print(line)
            if line.split(" ")[0] == "Referer:":
                content += line.split(" ")[1].replace(" ", "") + " "
            elif line.split(" ")[0] == "User-Agent:":
                content += line.split(":")[1].replace(" ", "") + " "

        content = content + "\n"

        with open(self.log_name, "a") as f:
            f.write(content)


class HTTPRequest:
    """Parser for HTTP requests. 
    
    It takes raw data and extracts meaningful information about the incoming request.

    Instances of this class have the following attributes:

        self.method: The current HTTP request method sent by client (string)

        self.uri: URI for the current request (string)

        self.http_version = HTTP version used by  the client (string)
    """

    def __init__(self, data):
        self.contents = None
        self.method = None
        self.uri = None
        self.http_version = '1.1'  # default to HTTP/1.1 if request doesn't provide a version
        self.message = None

        # call self.parse method to parse the request data
        self.parse(data)

    def parse(self, data):
        # 解析 HTTP request
        lines = data.split(b'\r\n')
        # 字符串类型的 HTTP request
        self.contents = data.decode('utf8').splitlines()

        request_line = lines[0]  # request line is the first line of the data

        words = request_line.split(b' ')  # split request line into separate words

        self.method = words[0].decode()  # call decode to convert bytes to string

        if len(words) > 1:
            # we put this in if block because sometimes browsers
            # don't send URI with the request for homepage
            self.uri = words[1].decode()  # call decode to convert bytes to string

        if len(words) > 2:
            # we put this in if block because sometimes browsers
            # don't send HTTP version
            self.http_version = words[2].decode()

        if len(lines) > 1:
            # the message content of post
            self.message = lines[-1].decode()


if __name__ == '__main__':
    server = TCPServer()
    server.start()
