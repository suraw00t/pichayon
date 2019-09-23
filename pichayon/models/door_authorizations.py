import mongoengine as me
import datetime


class GroupMember(me.EmbeddedDocument):
    group = me.ReferenceField('UserGroup',
                              dbref=True)
    granter = me.ReferenceField('User', dbref=True)
    started_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.now)
    expired_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.now)


class DoorAuthorizations(me.Document):
    door_group = me.ReferenceField('DoorGroup', dbref=True, required=True)

    user_group = me.ListField(me.EmbeddedDocumentField('GroupMember',
                                                       dbref=True))
    status = me.StringField(required=True, default='active')

    meta = {'collection': 'door_authorizations'}

    def is_member(self, group):
        for ugroup in self.user_group:
            if ugroup.group == group:
                return True
        return False

    def remove_member(self, group):
        for ugroup in self.user_group:
            print(ugroup.group)
            print(group)
            print(ugroup.group == group)
            # if ugroup.group == group:
            #     self.user_group.remove(ugroup)
