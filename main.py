import os
from wsgiref.simple_server import make_server


class WSGIMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        response_body_bytes = self.app(environ, start_response)
        response_body = " ".join(bytes.decode(x) for x in response_body_bytes)
        body_start_ind = response_body.find("<body>")
        response_body = response_body[:body_start_ind + 6] + "<div class='top'>Middleware TOP</div>" + \
                        response_body[body_start_ind + 6:]
        body_end_ind = response_body.find("</body>")
        response_body = response_body[:body_end_ind] + "<div class='botton'>Middleware BOTTOM</div>" +\
                        response_body[body_end_ind:]
        return [response_body.encode('utf-8')]


class WSGIApp:
    def __init__(self, static_dir):
        self.static_dir = static_dir

    def __call__(self, environ, start_response):
        headers = []
        response_body = ''
        if environ["REQUEST_METHOD"] != "GET":
            status = "501 Not Implemented"
            headers.append(("Content-Type", "text/plain"))
        else:
            resourse_addr = environ["PATH_INFO"][1:]
            if resourse_addr == "":
                resourse_addr = "index.html"
            try:
                with open(os.path.join(self.static_dir, resourse_addr)) as f:
                    response_body = f.read()
                    status = "200 OK"
            except FileNotFoundError:
                status = "404 Not Found"
                with open(os.path.join(self.static_dir, "404.html")) as f:
                    response_body = f.read()
            headers.append(("Content-Type", "text/html;charset=utf-8"))
            headers.append(("Content-Language", "en"))
            headers.append(("Content-Length", str(len(response_body))))
        start_response(status, headers)
        return [response_body.encode('utf-8')]


if __name__ == "__main__":
    wsgi_app = WSGIApp('static')
    wsgi_middleware = WSGIMiddleware(wsgi_app)
    wsgi_server = make_server('', 8000, wsgi_middleware)
    wsgi_server.serve_forever()





