import mongoengine as me
import datetime


class Rrule(me.EmbeddedDocument):
    days = me.ListField(me.IntField())
    start_time = me.StringField(required=True, default='8:00')
    end_time = me.StringField(required=True, default='17:00')


class AuthorizationGroup(me.EmbeddedDocument):
    user_group = me.ReferenceField('UserGroup',
                                   dbref=True)
    granter = me.ReferenceField('User', dbref=True)
    rrule = me.EmbeddedDocumentField('Rrule')
    started_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.now)
    expired_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.now)

    def check_rrule(self):
        if datetime.datetime.now() < self.started_date \
                or datetime.datetime.now() > self.expired_date:
            return False
        from dateutil.rrule import rrule, DAILY
        h_start, m_start, _ = self.rrule.start_time.split(':')
        expected_datetime = list(
                rrule(
                    freq=DAILY,
                    dtstart=datetime.datetime.combine(
                        datetime.date.today(),
                        datetime.time(0, 0)),
                    byweekday=self.rrule.days,
                    count=1,
                    byhour=int(h_start),
                    byminute=int(m_start),
                    bysecond=0))
        h_end, m_end, _ = self.rrule.end_time.split(':')
        exp_datetime = datetime.datetime.combine(datetime.date.today(),
                                                 datetime.time(int(h_end),
                                                               int(m_end)))
        print(expected_datetime)
        for dt in expected_datetime:
            if datetime.datetime.now() > dt \
                    and datetime.datetime.now() < exp_datetime:
                return True
        return False


class DoorAuthorization(me.Document):
    door_group = me.ReferenceField('DoorGroup', dbref=True, required=True)
    authorization_groups = me.ListField(
            me.EmbeddedDocumentField('AuthorizationGroup'))
    status = me.StringField(required=True, default='active')

    meta = {'collection': 'door_authorizations'}

    def is_group_member(self, group):
        for ugroup in self.authorization_groups:
            if ugroup.user_group == group:
                return True
        return False

    def is_user_member(self, user):
        for ugroup in self.authorization_groups:
            if ugroup.user_group.is_user_member(user):
                return True
        return False

    def is_authority(self, group):
        for ugroup in self.authorization_groups:
            if ugroup.user_group == group \
                    and datetime.datetime.now() < ugroup.expired_date \
                    and datetime.datetime.now() > ugroup.started_date \
                    and ugroup.check_rrule():
                return True
        return False

    def remove_member(self, user_group):
        for author_group in self.authorization_groups:
            if author_group.user_group == user_group:
                self.authorization_groups.remove(author_group)
                break
