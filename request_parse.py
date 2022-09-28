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
