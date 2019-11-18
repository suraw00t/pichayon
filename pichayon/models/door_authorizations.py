import mongoengine as me
import datetime


class Rrule(me.EmbeddedDocument):
    days = me.ListField(me.IntField())
    start_time = me.StringField(required=True, default='8:00')
    end_time = me.StringField(required=True, default='17:00')


class GroupMember(me.EmbeddedDocument):
    group = me.ReferenceField('UserGroup',
                              dbref=True)
    granter = me.ReferenceField('User', dbref=True)
    rrule = me.EmbeddedDocumentField('Rrule')
    started_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.now)
    expired_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.now)

    def check_rrule(self):
        from dateutil.rrule import rrule, WEEKLY
        h, m, _ = rrule.start_time.spilt(':')
        datetime_expected = list(rrule(freq=WEEKLY,
                                       dtstart=start,
                                       byweekday=rrule.days,
                                       count=1,
                                       byhour=h,
                                       byminute=m,
                                       bysecond=0))
        

class DoorAuthorizations(me.Document):
    door_group = me.ReferenceField('DoorGroup', dbref=True, required=True)
    user_group = me.ListField(me.EmbeddedDocumentField('GroupMember'))
    status = me.StringField(required=True, default='active')

    meta = {'collection': 'door_authorizations'}

    def is_group_member(self, group):
        for ugroup in self.user_group:
            if ugroup.group == group:
                return True
        return False

    def is_authority(self, group):
        for ugroup in self.user_group:
            if ugroup.group == group and datetime.datetime.now() < ugroup.expired_date and datetime.datetime.now() > ugroup.started_date:
                return True
        return False
