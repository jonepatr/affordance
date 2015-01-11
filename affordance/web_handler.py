import tornado.web
class WebHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")