import datetime
import asyncio
import json
import requests
from pichayon import models

import logging

logger = logging.getLogger(__name__)


class DataResourceManager:
    async def get_authorization_data(self, device_id):
        response = dict()
        door = models.Door.objects(device_id=device_id).first()

        if not door:
            logger.debug(f"client {device_id}: device is not found")
            return {}

        door_groups = door.get_door_groups()
        user_groups = door.get_allowed_user_groups()
        door_auths = door.get_authorizations()

        users = dict()

        for door_auth in door_auths:
            user_group = door_auth.user_group

            for member in user_group.get_user_group_members():
                # print('member', user_group)
                if member.user.id not in users:
                    users[member.user.id] = await self.render_json(
                        member.user, door_auth
                    )
                    users[member.user.id]["groups"] = []
                users[member.user.id]["groups"].append(str(member.user.id))

        response["action"] = "initial"
        response["users"] = list(users.values())
        return response

    async def get_authorization_user_data(self, user, user_group, door):
        # user = models.User.objects(id=user_id).first()
        # user_group = models.UserGroup.objects(id=user_group_id).first()
        # door = models.Door.objects(id=door_id).first()

        # if not user or not user_group or not door:
        #     return None

        if not user_group.is_user_member(user):
            logger.debug(f"{user.username} is not member of group {user_group.name}")
            return None

        door_auth = door.get_authorization_by_user_group(user_group)
        if not door_auth:
            logger.debug(f"door {door.name} is not authorized by {user_group.name}")
            return None

        return await self.render_json(user, door_auth)

    async def render_json(self, user, door_auth):

        user_group_member = door_auth.user_group.get_user_group_member(user)
        started_date = user_group_member.started_date
        expired_date = user_group_member.expired_date

        if not started_date or started_date > door_auth.started_date:
            started_date = door_auth.started_date

        if not expired_date or expired_date > door_auth.expired_date:
            expired_date = door_auth.expired_date

        data = {
            "id": str(user.id),
            "identifiers": [
                dict(
                    identifier=identity.identifier,
                    status=identity.status,
                )
                for identity in user.identities
                if identity.status == "active"
            ],
            "started_date": started_date.isoformat(),
            "expired_date": expired_date.isoformat(),
        }

        return data
