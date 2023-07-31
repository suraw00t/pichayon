import mongoengine as me
import datetime
from .doors import Door

# from .users import User


class UserGroupMember(me.Document):
    user = me.ReferenceField("User", dbref=True)
    group = me.ReferenceField("UserGroup", dbref=True)
    added_by = me.ReferenceField("User", dbref=True)
    role = me.StringField(required=True, default="member")
    added_date = me.DateTimeField(required=True, default=datetime.datetime.now)

    started_date = me.DateTimeField(required=True, default=datetime.datetime.now)
    expired_date = me.DateTimeField()

    updated_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True
    )

    application = me.ReferenceField("Application", dbref=True)

    meta = {"collection": "user_group_members"}


class UserGroup(me.Document):
    name = me.StringField(required=True, unique=True)
    description = me.StringField()
    creator = me.ReferenceField("User", dbref=True, required=True)

    created_date = me.DateTimeField(required=True, default=datetime.datetime.now)
    updated_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True
    )
    status = me.StringField(required=True, default="active")

    meta = {"collection": "user_groups"}

    def get_user_group_members(self):
        return UserGroupMember.objects(group=self)

    def get_user_group_member(self, user):
        return UserGroupMember.objects(group=self, user=user).first()

    def is_user_member(self, user):
        user_group_member = UserGroupMember.objects(user=user, group=self).first()
        if user_group_member:
            return True

        return False

    def is_supervisor(self, user):
        user_group_member = UserGroupMember.objects(user=user, group=self).first()
        if "superisor" == user_group_member.role:
            return True

        return False

    def get_group_authorizations(self):
        from .authorizations import GroupAuthorization

        return GroupAuthorization.objects(user_group=self)


class DoorGroup(me.Document):
    name = me.StringField(required=True, unique=True)
    description = me.StringField()
    default = me.BooleanField(default=False, required=True)
    doors = me.ListField(me.ReferenceField("Door", dbref=True))

    creator = me.ReferenceField("User", dbref=True, required=True)

    created_date = me.DateTimeField(required=True, default=datetime.datetime.now)
    updated_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True
    )
    status = me.StringField(required=True, default="active")

    meta = {"collection": "door_groups"}

    def get_door_members(self):
        return Door.objects(groups=self)

    def is_member(self, door):
        for member in self.members:
            if member == door:
                return True

        return False

    def search_device_id(self, device_id):
        for door in self.members:
            if door.device_id == device_id:
                return True
        return False

    def get_all_door_id(self):
        doors_id = []
        for door in self.members:
            doors_id.append(str(door.id))
        return doors_id
