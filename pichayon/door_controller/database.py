import asyncio
import logging
import pathlib

from tinydb import TinyDB, Query
import json

from tinydb.storages import JSONStorage
from tinydb_serialization import SerializationMiddleware
from tinydb_serialization.serializers import DateTimeSerializer

import datetime

logger = logging.getLogger(__name__)


class Manager:
    def __init__(self, settings, device_id):
        self.settings = settings
        dbpath = pathlib.Path(self.settings["TINYDB_STORAGE_PATH"])
        dbpath.parent.mkdir(parents=True, exist_ok=True)

        serialization = SerializationMiddleware(JSONStorage)
        serialization.register_serializer(DateTimeSerializer(), "TinyDate")

        self.db = TinyDB(str(dbpath), storage=serialization)
        self.user = self.db.table("users")
        self.log = self.db.table("logs")

        self.device_id = device_id

    # def initial_data_after_restart(self, data):
    #     logger.debug('Initial data')
    #     self.db.remove(self.query.type=='user')
    #     user_groups = data['user_groups']
    #     for group in user_groups:
    #         for member in group['members']:
    #             user = self.db.search(self.query.username==member['username'])
    #             if user:
    #                 continue
    #             self.db.insert({'username': member['username'], 'rfid': member['rfid'], 'passcode': member['passcode'], 'type':'user'})

    async def add_user(self, data):
        logger.debug(f"add user -> {data}")

        member = data.get("user")
        if not member:
            return

        member["started_date"] = datetime.datetime.fromisoformat(member["started_date"])
        member["expired_date"] = datetime.datetime.fromisoformat(member["expired_date"])

        User = Query()
        user = self.user.get(User.id == member["id"])
        if not user:
            self.user.insert(member)
        else:
            self.user.update(member)

    async def update_user(self, data):
        logger.debug(f"update user -> {data}")

        member = data.get("user")
        if not member:
            return

        member["started_date"] = datetime.datetime.fromisoformat(member["started_date"])
        member["expired_date"] = datetime.datetime.fromisoformat(member["expired_date"])

        User = Query()
        user = self.user.get(User.id == member["id"])
        if not user:
            return

        self.user.update(member)

    async def delete_user(self, data):
        logger.debug(f"delete user -> {data}")
        member = data.get("user")
        if not member:
            return

        User = Query()
        self.user.remove(User.id == member["id"])

    async def update_data(self, data):
        logger.debug("update data")
        users = data["users"]
        # for user in users:

        User = Query()

        for user in users:
            user["started_date"] = datetime.datetime.fromisoformat(user["started_date"])
            user["expired_date"] = datetime.datetime.fromisoformat(user["expired_date"])
            user = self.user.get(User.id == user["id"])
            if user:
                user.update(user)
                self.user.update(user)
            else:
                self.user.insert(user)

    async def initial_data(self, data):
        logger.debug("initial data")

        self.user.truncate()

        users = data["users"]

        for user in users:
            user["started_date"] = datetime.datetime.fromisoformat(user["started_date"])
            user["expired_date"] = datetime.datetime.fromisoformat(user["expired_date"])
            self.user.insert(user)

        logger.debug("end initial data")

    def __filter_rfid(self, ids, rfid_number, relex=True):
        for id in ids:
            if id["identifier"].upper() == rfid_number.upper():
                return True
            if id["identifier"][:-2].upper() == rfid_number.upper():
                return True

        return False

    async def get_user_by_rfid(self, rfid_number):
        User = Query()
        user = self.user.get(User.identifiers.test(self.__filter_rfid, rfid_number))

        return user

    async def get_user_by_rfid_with_current_date(self, rfid_number, relex=True):
        current_date = datetime.datetime.now()
        User = Query()
        user = self.user.get(
            User.identifiers.test(self.__filter_rfid, rfid_number, relex)
            & (User.started_date < current_date)
            & (User.expired_date >= current_date)
        )

        return user

    async def get_user_by_id_with_current_date(self, user_id):
        current_date = datetime.datetime.now()
        User = Query()
        user = self.user.get(
            (User.id == user_id)
            & (User.started_date < current_date)
            & (User.expired_date >= current_date)
        )

        return user

    async def put_log(self, log):
        self.log.insert(log)

    async def delete_log(self, log_id):
        Log = Query()
        self.log.remove(Log.id == log_id)

    async def get_waiting_logs(self):
        Log = Query()
        logs = self.log.search(Log.status == "wait")
        return logs
