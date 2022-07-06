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


class MessageThread(threading.Thread):
    def __init__(self, app):
        super().__init__()
        self.deamon = True

        self.app = app
        self.running = False

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.queue = asyncio.Queue()
        self.output_queue = queue.Queue()

    def stop(self):
        self.running = False
        # self.loop.stop()

        # self.loop.run_until_complete(self.queue.put(None))

    def put_data(self, data):
        # self.loop.create_task(self.put_to_queue(data))
        try:
            self.queue.put_nowait(data)
        except Exception as e:
            print(e)
            # check for queue empty
            pass

    # def request(self, topic, data):
    #     try:
    #         print('++++++++++++')

    #         raw_data = asyncio.run(
    #                 self.nc.request(
    #                     topic,
    #                     json.dumps(data).encode()
    #                     ))
    #         print('-------------')
    #         data = json.load(raw_data.decode())
    #     except Exception as e:
    #         print(e)
    #     print('-----<>', data)
    #     return data

    async def put_to_queue(self, data):
        await self.queue.put(data)

    async def initial_nats_client(self):
        self.nc = NATS()
        await self.nc.connect(
            current_app.config.get("PICHAYON_MESSAGE_NATS_HOST"),
            max_reconnect_attempts=-1,
            reconnect_time_wait=2,
        )

    async def run_async_loop(self):
        await self.initial_nats_client()

        while self.running:
            data = None

            try:
                data = self.queue.get_nowait()
            except Exception as e:
                await asyncio.sleep(0.1)
                continue

            if not data:
                continue

            message = data.get("message", {})
            msg_type = data.get("type", "publish")

            print("-->", message)

            if msg_type == "publish":
                await self.nc.publish(data.get("topic"), json.dumps(message).encode())
            elif msg_type == "request":
                try:
                    msg = await self.nc.request(
                        data.get("topic"), json.dumps(message).encode()
                    )
                    raw_data = msg.data.decode()
                    self.output_queue.put(json.loads(raw_data))
                except Exception as e:
                    print("request error:", e)

    def run(self):
        self.running = True
        with self.app.app_context():
            # self.loop.create_task(self.run_async_loop())
            # self.loop.run_forever()

            self.loop.run_until_complete(self.run_async_loop())


class NatsClient:
    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_nats(self, app):
        message_thread = MessageThread(app)
        s = {"app": app, "thread": message_thread}
        app.extensions["pichayon_nats"][self] = s
        message_thread.start()

    def init_app(self, app):
        self.app = app

        app.extensions = getattr(app, "extensions", {})

        if "pichayon_nats" not in app.extensions:
            app.extensions["pichayon_nats"] = {}

        @app.before_first_request
        def start_thread():

            if self in app.extensions["pichayon_nats"]:
                self.stop()

            self.init_nats(app)

        atexit.register(self.stop)

    def stop(self):
        if self in self.app.extensions["pichayon_nats"]:
            self.app.extensions["pichayon_nats"][self]["thread"].stop()

    def publish(self, topic: str, message: str):
        t = self.app.extensions["pichayon_nats"][self]["thread"]
        t.put_data(dict(topic=topic, message=message, type="publish"))

    def request(self, topic: str, message: str):
        t = self.app.extensions["pichayon_nats"][self]["thread"]
        message_id = time.time()
        message["message_id"] = message_id
        t.put_data(dict(topic=topic, message=message, type="request"))
        try:
            counter = 0
            while counter < 30:
                if t.output_queue.empty():
                    time.sleep(0.01)
                    counter += 1
                    continue

                data = t.output_queue.get()
                if data["message_id"] == message_id:
                    message = data
                    break
                elif data["message_id"] != message_id:
                    if data["message_id"] - message_id < 10:
                        t.output_queue.put(data)

        except Exception as e:
            print("->", e)

        return message


nats_client = NatsClient()


def init_nats(app):
    nats_client.init_app(app)
