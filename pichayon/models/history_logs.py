import mongoengine as me
import datetime


class HistoryLog(me.Document):
    actor = me.ReferenceField('User', dbref=True)
    user = me.ReferenceField('User', dbref=True)
    action = me.StringField()
    door_group = me.StringField()
    user_group = me.StringField()
    recorded_date = me.DateTimeField(required=True,
                                     default=datetime.datetime.now)

    meta = {'collection': 'history_logs'}

