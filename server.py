import http.server
import socketserver
import tts

class MyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('web-ui.html', 'rb') as file:
                self.wfile.write(file.read())

    def do_POST(self):
        if self.path == '/process':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            params = post_data.decode('utf-8') 

            output_text = tts.llm(params) # input for gpt

            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(bytes(output_text, 'utf-8'))

            tts.tts(output_text) # output to tts


PORT = 8000

class MyTCPServer(socketserver.TCPServer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.input_text = ""

with MyTCPServer(("", PORT), MyHandler) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()
