import datetime
import asyncio
import json
import requests
from pichayon import models

import logging
logger = logging.getLogger(__name__)

class DataResourceManager:
    async def get_authorization_data(self, device_id):
        door_groups = models.DoorGroup.objects()
        door_auth = None
        ugroup = list()
        ugroup_selected = dict()
        # logger.debug('data res1')
        for door_group in door_groups:
            # logger.debug(door_group.name)
            if door_group.search_device_id(device_id):
                door_auth = models.DoorAuthorizations.objects(door_group=door_group).first()
                # logger.debug(door_auth)
                break
        if door_auth is None:
            return {}
        # logger.debug('res2')
        for user_group in door_auth.user_group:
            # logger.debug(user_group.group)
            ugroup.append(user_group.group)
        
        for group in ugroup:
            # logger.debug('res3')
            if door_auth.is_authority(group):
                ugroup_selected['name'] = group.name
                ugroup_selected['members'] = list()
                for member in group.members:
                    ugroup_selected['members'].append({'username': member.user.username})

    
        # logger.debug('res5')
        # logger.debug(ugroup_selected)
        return ugroup_selected
