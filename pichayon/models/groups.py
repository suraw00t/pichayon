import mongoengine as me
import datetime

# from .users import User


class GroupMember(me.EmbeddedDocument):
    user = me.ReferenceField('User', dbref=True)
    added_by = me.ReferenceField('User', dbref=True)
    added_date = me.DateTimeField(required=True,
                                  default=datetime.datetime.utcnow)


class Group(me.Document):
    name = me.StringField(required=True, unique=True)
    description = me.StringField()

    members = me.ListField(me.EmbeddedDocumentField('GroupMember'))

    created_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.utcnow)
    updated_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.utcnow,
                                    auto_now=True)
    status = me.StringField(required=True, default='active')

    meta = {'collection': 'groups'}

    def is_member(self, user):
        for member in self.members:
            if member.user == user:
                return True

        return False
