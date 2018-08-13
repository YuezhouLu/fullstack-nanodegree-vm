from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer


class myWebServerHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        if self.path.endswith('/hi'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            message = ""
            message += "<html><body>Hi, there! You have successfully done this! Great Job!</body></html>"
            self.wfile.write(message)
            print message
            return
        
        else:
            self.send_error(404, 'File Cannot be Found at: %s' % self.path)
            print "404 Error!"


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), myWebServerHandler)
        print "myWebServer is running on port %s" % port
        server.serve_forever()
    
    except KeyboardInterrupt:
        print "^C Entered! Stop running myWebServer..."
        server.socket.close()


if __name__ == '__main__':
    main()