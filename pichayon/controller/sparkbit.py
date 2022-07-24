import datetime
import asyncio
import logging
import requests

from cloudant.client import Cloudant

from pichayon import models

logger = logging.getLogger(__name__)


class DoorController:
    def __init__(self, settings):
        self.settings = settings

        self.client = Cloudant(
            settings.get("SPARKBIT_API_DATABASE_USERNAME"),
            settings.get("SPARKBIT_API_DATABASE_PASSWORD"),
            url=settings.get("SPARKBIT_API_DATABASE_URL"),
            connect=True,
            auto_renew=True,
        )
        self.command_queue = asyncio.Queue()
        self.running = False

        self.door_status_url = settings.get("SPARKBIT_API_DOOR_STATUS")
        self.door_lock_url = settings.get("SPARKBIT_API_DOOR_LOCK")
        self.door_unlock_url = settings.get("SPARKBIT_API_DOOR_UNLOCK")

    async def put_command(self, data):
        await self.command_queue.put(data)

    async def process_command(self):
        self.running = True
        while self.running:
            command = await self.command_queue.get()
            logger.debug(f"sparkbit process {command}")
            action = command.get("action", None)
            if not action:
                return

            if action == "list":
                db = self.client["door-r202-test"]
                logger.debug("all document")
                for document in db:
                    logger.debug(document)
            if action == "add-user":
                await self.add_user(command)
            elif action == "delete-user":
                await self.delete_user(command)
            elif action == "update-user":
                await self.update_user(command)
            elif action == "open-door":
                await self.open_door(command)

    def stop(self):
        self.running = False
        self.command_queue.put({})

        self.client.disconnect()

    async def delete_user(self, command):
        try:
            door = models.Door.objects.get(id=command["door"].get("id"))
            user = models.User.objects.get(id=command["user"].get("id"))
            sparkbit_door = models.SparkbitDoorSystem.objects.get(door=door)
        except Exception as e:
            logger.exception(e)
            return

        db = self.client[sparkbit_door.device_id]
        # doc = db.get_document(f'user-{user.system_id}')
        key = f"user-{user.system_id}"
        if key not in db or not db[key].exists():
            logger.debug(
                f"there are no user {user.system_id} in database {sparkbit_door.device_id}"
            )
            return
        doc = db[key]
        doc.fetch()
        doc.delete()
        logger.debug(f"sparkbit delete {user.system_id} success")

    async def open_door(self, command):
        door = models.Door.objects.get(id=command.get("door_id"))
        user = models.User.objects.get(id=command.get("user_id"))
        sparkbit_door = models.SparkbitDoorSystem.objects(door=door).first()

        if not sparkbit_door:
            logger.debug(
                f'door id {command.get("door_id")} is not sparkbit member {command}'
            )
            return

        db = self.client[sparkbit_door.device_id]
        if not "user-{}".format(user.system_id) in db:
            logger.debug(f"user {user.system_id} is not in db")
            return

        try:
            # response = requests.post(
            #         self.door_unlock_url.format(
            #             sparkbit_door.device_id.replace('door-', '')),
            #         verify=False)
            # logger.debug(response.status_code)
            # if response.status_code != 200:
            #     logger.debug(f'door {user.system_id} is not open')
            #     return

            db = self.client[sparkbit_door.device_id]
            if "status" not in db:
                logger.debug(f"door {user.system_id} is not open -> no status")

            status = db["status"]
            status.fetch()

            if status["doorState"] != "closed":
                logger.debug(
                    f'door {user.system_id} is not open -> status {status["doorState"]}'
                )
                return

            status["lockState"] = "unlocked"
            status.save()

            logger.debug(f"door {user.system_id} is open")
        except Exception as e:
            logger.debug(e)

    async def add_user(self, command):
        door = None
        data = command["user"]
        try:
            user = models.User.objects.get(id=data.get("id"))
            door = models.Door.objects.get(id=command.get("door_id"))
            sparkbit_door = models.SparkbitDoorSystem.objects.get(door=door)

        except Exception as e:
            logger.exception(e)

        db = self.client[sparkbit_door.device_id]
        key = f"user-{user.system_id}"
        if key in db and db[key].exists():
            logger.debug(f"this user {user.system_id} available in sparkbit")
            return

        user_data = await self.get_document(user, data)
        doc = db.create_document(user_data)
        logger.debug(f"sparkbit add {user.system_id} success")

    async def update_user(self, command):
        door = None
        user_data = command["user"]
        door_data = command["door"]
        try:
            user = models.User.objects.get(id=user_data.get("id"))
            door = models.Door.objects.get(id=door_data.get("id"))
            sparkbit_door = models.SparkbitDoorSystem.objects(door=door).first()

        except Exception as e:
            logger.exception(e)
            return

        if not sparkbit_door:
            return

        db = self.client[sparkbit_door.device_id]
        key = f"user-{user.system_id}"
        if key not in db or (key in db and not db[key].exists()):
            # logger.debug(f"this user {user.system_id} is available in sparkbit")
            # return

            adding_command = dict(
                user=command.get("user"), door_id=command["door"]["id"]
            )
            await self.add_user(adding_command)
            return

        doc = db[key]
        doc.fetch()
        # need to decision
        user_data = await self.get_document(user, user_data)

        doc.update(user_data)
        doc.save()
        logger.debug(f"sparkbit update {user.system_id} success")

    async def get_document(self, user, data):

        started_date = int(
            datetime.datetime.fromisoformat(data["started_date"]).timestamp() * 1000
        )
        ended_date = int(
            datetime.datetime.fromisoformat(data["expired_date"]).timestamp() * 1000
        )

        response_data = dict(
            _id="user-{}".format(user.system_id),
            thFirstName=user.first_name_th,
            thLastName=user.last_name_th,
            enFirstName=user.first_name,
            enLastName=user.last_name,
            idCardNumber=user.id_card_number,
            calendarsEvents=[
                dict(
                    startDate=started_date,
                    duration=86400000,
                    endDate=ended_date,
                    rRule=dict(type="text", value="every day"),
                )
            ],
            isAdmin=False,
            mifareCards=dict(),
            nfcDevices=dict(),
            pin="",
        )

        if not user.username.isdigit():
            for id in user.identities:
                id_data = {f"{id.identifier}": {}}
                response_data["mifareCards"][f"{id.identifier}"] = dict(
                    enabled=True if id.status == "active" else False,
                    deactivated=False,
                )
        return response_data

    async def get_state(self, command):
        door_data = command["door"]

        try:
            door = models.Door.objects.get(id=door_data.get("id"))
            sparkbit_door = models.SparkbitDoorSystem.objects(door=door).first()

        except Exception as e:
            logger.exception(e)
            return

        if not sparkbit_door:
            return command

        db = self.client[sparkbit_door.device_id]

        doc = db["status"]
        doc.fetch()
        door_data["state"] = doc["doorState"]

        return command
