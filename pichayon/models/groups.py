import mongoengine as me
import datetime

# from .users import User


class UserMember(me.EmbeddedDocument):
    user = me.ReferenceField('User', dbref=True)
    role = me.StringField(required=True, default='Member')
    added_by = me.ReferenceField('User', dbref=True)
    added_date = me.DateTimeField(required=True,
                                  default=datetime.datetime.now)


class UserGroup(me.Document):
    name = me.StringField(required=True, unique=True)
    description = me.StringField()
    members = me.ListField(me.EmbeddedDocumentField('UserMember'))

    created_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.now)
    updated_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.now,
                                    auto_now=True)
    status = me.StringField(required=True, default='active')

    meta = {'collection': 'user_groups'}

    def is_member(self, user):
        for member in self.members:
            if member.user == user:
                return True
        return False

    def is_supervisor(self, user):
        for member in self.members:
            if member.user == user and 'Member' not in member.role:
                return True

        return False

class DoorGroup(me.Document):
    name = me.StringField(required=True, unique=True)
    description = me.StringField()

    members = me.ListField(me.ReferenceField('Door', dbref=True))

    created_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.now)
    updated_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.now,
                                    auto_now=True)
    status = me.StringField(required=True, default='active')

    meta = {'collection': 'door_groups'}

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

