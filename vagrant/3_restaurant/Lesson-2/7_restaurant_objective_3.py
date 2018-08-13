from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

# Import modules for CRUD operations from lesson-1
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

# Create session and connect to DB
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()


class WebServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path.endswith("/restaurants"):
                restaurants = session.query(Restaurant).all()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<a href = restaurants/new> Make a New Restaurant Here </a><br><br>"
                for restaurant in restaurants:
                    output += "%s" % restaurant.name
                    output += "<br>"
                    output += "<a href = '#'>Edit</a>"
                    output += "<br>"
                    output += "<a href = '#'>Delete</a>"
                    output += "<br><br><br>"
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>Make A New Restaurant!</h1>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/restaurants/new'>
                            <input name="newRestaurantName" type="text" placeholder="New Restaurant Name">
                            <button type="submit">Create!</button>
                            </form>'''
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return
            
            if self.path.endswith("/hello"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                message = ""
                message += "<html><body>Hello!"
                message += '''<form method='POST' enctype='multipart/form-data' action='/hello'>
                            <h2>What would you like me to say?</h2>
                            <input name="message" type="text" value="Say something...">
                            <button type="submit">Submit</button>
                            </form>'''
                message += "</body></html>"
                self.wfile.write(message)
                print message
                return

            if self.path.endswith("/hola"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                message = ""
                message += "<html><body>&#161Hola! <a href = /hello>Back to Hello</a></body></html>"
                message += '''<form method='POST' enctype='multipart/form-data' action='/hello'>
                            <h2>What would you like me to say?</h2>
                            <input name="message" type="text" value="Say something...">
                            <button type="submit">Submit</button>
                            </form>'''
                message += "</body></html>"
                self.wfile.write(message)
                print message
                return
        
        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)


    def do_POST(self):
        try:
            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('Content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    newRestaurantName = fields.get('newRestaurantName')
                
                # Create new Restaurant class
                newRestaurant = Restaurant(name = newRestaurantName[0])
                session.add(newRestaurant)
                session.commit()

                # Create a redirect
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()

                return

            # self.send_response(301)
            # self.send_header('Content-type', 'text/html')
            # self.end_headers()
            # ctype, pdict = cgi.parse_header(self.headers.getheader('Content-type'))
            # if ctype == 'multipart/form-data':
            #     fields = cgi.parse_multipart(self.rfile, pdict)
            #     messagecontent = fields.get('message')
            # output = ""
            # output += "<html><body>"
            # output += "<h2>Okay, how aout this:</h2>"
            # output += "<h1>%s</h1>" % messagecontent[0]
            # output += '''<form method='POST' enctype='multipart/form-data' action='/holala'>
            #                 <h2>What do you want me to say?</h2>
            #                 <input name="message" type="text" value="Please say something...">
            #                 <button type="submit">Submit!</button>
            #                 </form>'''
            # output += "</html></body>"
            # self.wfile.write(output)
            # print output
        
        except:
            pass

def main():
    try:
        port = 8080
        server = HTTPServer(('', port), WebServerHandler)
        print "Web Server running on port %s" % port
        server.serve_forever()
    
    except KeyboardInterrupt:
        print " ^C entered, stopping web server...."
        server.socket.close()

if __name__ == '__main__':
    main()