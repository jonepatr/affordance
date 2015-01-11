#!/usr/bin/python
# -*- coding: utf-8 -*-

""" This module is used for optitrack + ems"""

import os
import tornado.ioloop
from unity import Unity
from web_handler import WebHandler
from websocket_handler import WebsocketHandler


def main():
    """Main function of program"""
    uni = Unity()
    uni.start()
    application = tornado.web.Application(
        [
            (r"/", WebHandler),
            (r"/websocket", WebsocketHandler, dict(uni=uni)),
        ],
        template_path=os.path.join(os.path.dirname(__file__), "../www"),
        static_path=os.path.join(os.path.dirname(__file__), "../www/static"),
        debug=True
    )
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()


