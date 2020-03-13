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
        res = dict()
        door_auth = None
        ugroup = list()
        ugroup_selected = dict()
        door = models.Door.objects(device_id=device_id).first()
        logger.debug('data res1')
        for door_group in door_groups:
            # logger.debug(door_group.name)
            if door_group.search_device_id(device_id):
                door_auth = models.DoorAuthorization.objects(door_group=door_group).first()
                # logger.debug(door_auth)
                break
        if door_auth is None:
            return {}
        logger.debug('res2')
        for authorization_group in door_auth.authorization_groups:
            logger.debug(authorization_group.user_group.name)
            ugroup.append(authorization_group.user_group)
        
        res['user_groups'] = list()
        for group in ugroup:
            logger.debug('res3')
            if door_auth.is_authority(group):
                logger.debug('res4')
                ugroup_selected['name'] = group.name
                ugroup_selected['members'] = list()
                members = models.UserGroupMember.objects(group=group)
                for member in members:

                    ugroup_selected['members'].append(
                            {'username': member.user.username,
                             'rfid':member.user.rfid})
                res['user_groups'].append(ugroup_selected)

        res['passcode'] = door.passcode
        res['action'] = 'update'
        logger.debug(res)
        # logger.debug(ugroup_selected)
        return res
