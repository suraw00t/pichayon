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
            logger.debug(f'client {device_id}: device is not found')
            return {}

        door_groups = door.get_door_groups()
        user_groups = door.get_allowed_user_groups()
        door_auths = door.get_authorization()

        response['user_groups'] = list()
        for door_auth in door_auths:
            user_group = door_auth.user_group
            user_group_info = dict(
                    name=user_group.name,
                    members=list(),
                    )

            for member in user_group.get_user_group_members():
                print('member', user_group)
                user_group_info['members'].append(
                        {
                            'id': str(member.user.id),
                            'username': member.user.username,
                            'identifiers': [
                                dict(
                                    identifier=identity.identifier,
                                    status=identity.status,
                                    ) 
                                for identity in member.user.identities \
                                        if identity.status == 'active'
                                ],
                            'started_date': door_auth.started_date.isoformat(),
                            'expired_date': door_auth.expired_date.isoformat(),
                        }
                    )
            
            response['user_groups'].append(user_group_info)
        print('xxx', response)
        response['action'] = 'initial'
        return response
