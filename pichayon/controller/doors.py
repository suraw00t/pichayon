import asyncio
import logging
import json
from nats.aio.client import Client as NATS
from pichayon import models
import datetime

logger = logging.getLogger(__name__)
from . import data_resources
from . import sparkbit


class DoorManager:
    def __init__(self, data_resource):
        self.nc = None
        self.sparkbit_enable = False
        self.data_resource = data_resource

    async def set_sparkbit_status(self, status: bool):
        self.sparkbit_enable = status

    async def set_message_client(self, nc):
        self.nc = nc

    async def handle_door_controller_greeting(self, msg):
        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()

        data = json.loads(data)
        logger.debug(f"door manager process -> {data}")
        if data["action"] == "register":
            # logger.debug('before res')
            logger.debug(f'client {data["device_id"]} is registering')
            # response = await self.data_resource.get_authorization_data(data['device_id'])
            # logger.debug('after res')
            door = models.Door.objects(device_id=device_id).first()
            response = data
            if door:
                response["status"] = "registed"
                registed["completed_date"] = datetime.datetime.now()
                door.device_updated_date = datetime.datetime.now()
                door.save()
            else:
                response["status"] = "rejected"

            await self.nc.publish(reply, json.dumps(response).encode())
            logger.debug("client {} is registed".format(data["device_id"]))

    # async def update_data_to_door_controller(self):
    #     while self.running:
    #         logger.debug('start sync data')
    #         doors = models.Door.objects(status='active', type='pichayon')
    #         for door in doors:
    #             logger.debug(f' {door.device_id}')
    #             if len(door.device_id) == 0:
    #                 continue

    #             topic = f'pichayon.door_controller.{door.device_id}'
    #             response = await self.data_resource.get_authorization_data(door.device_id)

    #             await self.nc.publish(
    #                     topic,
    #                     response,
    #                     )

    #         logger.debug('end sync sleep')
    #         await asyncio.sleep(3600)

    async def open(self, data):
        door = models.Door.objects.get(id=data["door_id"])
        user = models.User.objects.get(id=data["user_id"])

        if not door.is_allow(user):
            logger.debug("No Authority")
            return

        if "sparkbit" in door.device_type:
            if not self.sparkbit_enable:
                logger.debug("Sparkbit Disable")
                return

            logger.debug("open sparkbit")
            topic = "pichayon.controller.sparkbit.command"
            command = dict(
                door_id=data["door_id"], user_id=data["user_id"], action="open"
            )
            logger.debug("set success")
        else:
            topic = f"pichayon.door_controller.{door.device_id}"
            command = dict(
                device_id=door.device_id, user_id=data["user_id"], action="open"
            )

        try:
            await self.nc.publish(topic, json.dumps(command).encode())
        except Exception as e:
            logger.exception(e)

        logger.debug("Send Success")

    async def get_state(self, data):
        door = models.Door.objects.get(id=data["door_id"])

        if "sparkbit" in data["device_type"]:
            if not self.sparkbit_enable:
                logger.debug("Sparkbit Disable")
                return

            logger.debug("open sparkbit")
            topic = "pichayon.controller.sparkbit.command"
            command = dict(
                door_id=data["door_id"], user_id=data["user_id"], action="open"
            )
            logger.debug("set success")
        else:
            topic = f"pichayon.door_controller.{door.device_id}"
            command = dict(
                device_id=door.device_id, user_id=data["user_id"], action="open"
            )

        try:
            await self.nc.publish(topic, json.dumps(command).encode())
        except Exception as e:
            logger.exception(e)
        logger.debug("Send Success")

    async def process_door_controller_log(self, msg):
        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()
        data = json.loads(data)

        device_id = data["device_id"]
        door = models.Door.objects(device_id=device_id).first()
        log = data["log"]
        log["status"] = "completed"
        log["log_date"] = datetime.datetime.fromisoformat(log["log_date"])

        history_log = models.HistoryLog(
            actor=log["actor"],
            door=door,
            action=log["action"],
            details=log,
            log_date=log["log_date"],
            message=log.get("message", ""),
        )

        if log["actor"] != "system":
            history_log.user = models.User.objects(id=log["user_id"]).first()

        # logger.debug('3 loop')
        history_log.save()

        # logger.debug('4 loop')

        response = dict(status="OK")
        await self.nc.publish(
            reply,
            json.dumps(response).encode(),
        )

    async def add_member_to_group(self, data):
        logger.debug("try to add member")

        user_group = models.UserGroup.objects(id=data["user_group_id"]).first()
        if not user_group:
            logger.debug(f'user group: {data["user_group_id"]} not found')
            return

        auth_groups = models.GroupAuthorization.objects(
            user_group=user_group,
        )

        users = models.User.objects(id__in=data["user_ids"])
        for user in users:
            if not user_group.is_user_member(user):
                logger.debug(f"{user.username} is not member of {user_group.name}")
                return

        for auth_group in auth_groups:
            for door in auth_group.door_group.doors:
                print(door.id, door.name)
                for user in users:
                    data = await self.data_resource.get_authorization_user_data(
                        user, user_group, door
                    )
                    if not data:
                        logger.debug(f"user {user.username} is not allow")
                        return

                    command = dict(
                        action="add-user",
                        user=data,
                    )

                    topic = f"pichayon.door_controller.{door.device_id}"
                    if door.device_type == "sparkbit":
                        command["door_id"] = str(door.id)
                        topic = f"pichayon.controller.sparkbit.command"

                    await self.nc.publish(
                        topic,
                        json.dumps(command).encode(),
                    )

        logger.debug("end adding member")

    async def delete_member_from_group(self, data):
        logger.debug("try to delete member")

        user_group = models.UserGroup.objects(id=data["user_group_id"]).first()
        if not user_group:
            logger.debug(f'user group: {data["user_group_id"]} not found')
            return

        auth_groups = models.GroupAuthorization.objects(
            user_group=user_group,
        )

        user = models.User.objects(id=data["user_id"])
        if not user:
            logger.debug(f'user id: {data["user_id"]} not found')
            return

        data = dict(id=data["user_id"])
        for auth_group in auth_groups:
            for door in auth_group.door_group.doors:

                command = dict(
                    action="delete-user",
                    user=data,
                )

                topic = f"pichayon.door_controller.{door.device_id}"
                if door.device_type == "sparkbit":
                    topic = f"pichayon.controller.sparkbit.command"
                    command["door"] = dict(id=str(door.id))

                await self.nc.publish(
                    topic,
                    json.dumps(command).encode(),
                )

    async def update_member(self, data):
        logger.debug("try to update member")
        user = models.User.objects(id=data.get("user_id")).first()

        if not user:
            logger.debug("user not found")
            return

        user_groups = user.get_user_groups()

        doors = []
        for user_group in user_groups:
            for auth_group in user_group.get_group_authorizations():
                for door in auth_group.door_group.doors:

                    if door not in doors:
                        doors.append(door)
                    else:
                        continue

                    data = await self.data_resource.get_authorization_user_data(
                        user, user_group, door
                    )
                    command = dict(
                        action="update-user",
                        user=data,
                    )

                    topic = f"pichayon.door_controller.{door.device_id}"
                    if door.device_type == "sparkbit":
                        topic = f"pichayon.controller.sparkbit.command"
                        command["door"] = dict(id=str(door.id))

                    await self.nc.publish(
                        topic,
                        json.dumps(command).encode(),
                    )

    async def update_authorization(self, data):
        print("update authorization", data)

    async def delete_authorization(self, data):
        print("act delete authorization", data)
