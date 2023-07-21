import mongoengine as me
import datetime


class Door(me.Document):
    name = me.StringField(required=True, max_length=250)
    description = me.StringField()
    camera_url = me.StringField(default="", required=True)
    # passcode = me.StringField(default='')
    # groups = me.ListField(me.ReferenceField('DoorGroup'))

    creator = me.ReferenceField("User", dbref=True)
    is_web_open = me.BooleanField(default=False, required=True)
    is_passcode = me.BooleanField(default=False, required=True)
    is_auto_relock = me.BooleanField(default=True, required=True)

    status = me.StringField(required=True, default="active")

    device_type = me.StringField(required=True, default="pichayon")
    device_id = me.StringField(unique=True, max_length=250)
    device_updated_date = me.DateTimeField()

    created_date = me.DateTimeField(required=True, default=datetime.datetime.now)
    updated_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True
    )

    meta = {"collection": "doors"}

    def is_allow(self, user):
        from . import groups
        from . import authorizations

        door_groups = groups.DoorGroup.objects(doors=self)
        user_group_members = groups.UserGroupMember.objects(user=user)

        user_groups = [ugm.group for ugm in user_group_members]
        group_auths = authorizations.GroupAuthorization.objects(
            door_group__in=door_groups,
            user_group__in=user_groups,
        )

        # print('--->', group_auths)

        if group_auths:
            return True

        return False

    def get_authorization_by_user_group(self, user_group):
        from . import groups
        from . import authorizations

        door_groups = groups.DoorGroup.objects(doors=self)

        group_auth = authorizations.GroupAuthorization.objects(
            door_group__in=door_groups,
            user_group=user_group,
        ).first()

        return group_auth

    def get_authorizations(self):
        from . import authorizations

        door_groups = self.get_door_groups()
        door_auths = authorizations.GroupAuthorization.objects(
            door_group__in=door_groups
        )

        return door_auths

    def get_allowed_user_groups(self):
        door_auths = self.get_authorizations()

        return [door_auth.user_group for door_auth in door_auths]

    def get_door_attributes(self):
        if type == "sparkbit":
            return models.SparkbitDoorSystem.object.get(door=self)

        return None

    def get_door_groups(self):
        from . import groups

        return groups.DoorGroup.objects(doors=self)

    def get_state(self):
        from . import history_logs

        history_log = (
            history_logs.HistoryLog.objects(
                door=self,
                action="door-status",
            )
            .order_by("-id")
            .first()
        )
        if history_log:
            return history_log.details.get("state", "unknow")

        return "unknow"
