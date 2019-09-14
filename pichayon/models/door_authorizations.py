import mongoengine as me
import datetime

class DoorAuthorizations(me.Document):
    door_group = me.ReferenceField('DoorGroup', dbref=True, required=True)
    granter = me.ReferenceField('User', dbref=True)
    user_group = me.ListField(me.ReferenceField('UserGroup',
                                                dbref=True))
    started_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.now)
    expired_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.now)

    status = me.StringField(required=True, default='active')

    meta = {'collection': 'door_authorizations'}

    def is_member(self, group):
        for ugroup in self.user_group:
            if ugroup == group:
                return True
        return False
