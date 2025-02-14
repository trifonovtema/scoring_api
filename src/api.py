#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import uuid
from argparse import ArgumentParser
from http.server import BaseHTTPRequestHandler, HTTPServer

from src.handler import method_handler
from src.setup_logs import setup_logging
from src.settings import Responses, store_settings
from src.store import Store


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {"method": method_handler}
    store = Store(host=store_settings.host, port=store_settings.port)

    def get_request_id(self, headers):
        return headers.get("HTTP_X_REQUEST_ID", uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, Responses.OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers["Content-Length"]))
            request = json.loads(data_string)
        except Exception as e:
            logging.exception("Unexpected error: %s" % e)
            code = Responses.BAD_REQUEST

        if request is not None:
            path = self.path.strip("/")
            logging.info("%s: %s %s" % (self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    response, code = self.router[path](
                        {"body": request, "headers": self.headers}, context, self.store
                    )
                except Exception as e:
                    logging.exception("Unexpected error: %s" % e)
                    code = Responses.INTERNAL_ERROR
            else:
                code = Responses.NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in Responses.ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {
                "error": response or Responses.ERRORS.get(code, "Unknown Error"),
                "code": code,
            }
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r).encode("utf-8"))
        return

    def do_GET(self):
        if self.path == "/healthcheck":
            try:
                self.store.client.ping()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                response = {"status": "ok", "message": "Server is healthy"}
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                response = {"status": "error", "message": str(e)}

            self.wfile.write(json.dumps(response).encode("utf-8"))
        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {"error": "Not Found"}
            self.wfile.write(json.dumps(response).encode("utf-8"))


if __name__ == "__main__":
    setup_logging()
    parser = ArgumentParser()
    parser.add_argument("-p", "--port", action="store", type=int, default=8080)
    parser.add_argument("-l", "--log", action="store", default=None)
    args = parser.parse_args()
    server = HTTPServer(("0.0.0.0", args.port), MainHTTPHandler)
    logging.info("Starting server at %s" % args.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
    logging.info("Stopping server at %s" % args.port)
