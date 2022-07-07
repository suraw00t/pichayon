import asyncio

from nats.aio.client import Client as NATS

import flask
from flask import current_app

import threading
import asyncio
import atexit
import json
import time
import queue


class NatsClient:
    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_nats(self, app):

        nc = NATS()

        loop = asyncio.new_event_loop()
        loop.run_until_complete(
            nc.connect(
                current_app.config.get("PICHAYON_MESSAGE_NATS_HOST"),
                max_reconnect_attempts=-1,
                reconnect_time_wait=2,
            )
        )

        s = {"app": app, "client": nc, "loop": loop}
        app.extensions["nats"][self] = s

    def init_app(self, app):
        self.app = app

        @app.before_first_request
        def init_nats_client():
            print("init nats client")
            if "nats" not in app.extensions:
                app.extensions["nats"] = {}

            if self in app.extensions["nats"]:
                self.stop()

            self.init_nats(app)

        atexit.register(self.stop)

    def stop(self):
        if "nats" not in self.app.extensions:
            print("nats not in extensions")
            return

        if self in self.app.extensions["nats"]:
            loop = self.app.extensions["nats"][self]["loop"]
            loop.run_until_complete(self.app.extensions["nats"][self]["client"].close())

        self.app.extensions.pop("nats")

    def publish(self, topic: str, message: dict):
        client = self.app.extensions["nats"][self]["client"]
        loop = self.app.extensions["nats"][self]["loop"]
        if not loop.is_running():
            init_nats(self.app)
            loop = self.app.extensions["nats"][self]["loop"]

        loop.run_until_complete(client.publish(topic, json.dumps(message).encode()))

    def request(self, topic: str, message: dict):
        client = self.app.extensions["nats"][self]["client"]
        loop = self.app.extensions["nats"][self]["loop"]
        if not loop.is_running():
            init_nats(self.app)
            loop = self.app.extensions["nats"][self]["loop"]

        msg = loop.run_until_complete(
            client.request(topic, json.dumps(message).encode(), timeout=1)
        )
        return json.loads(msg.data.decode())


nats_client = NatsClient()


def init_nats(app):
    nats_client.init_app(app)
