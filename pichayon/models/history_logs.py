import mongoengine as me
import datetime


class HistoryLog(me.Document):
    actor = me.StringField(required=True)
    user = me.ReferenceField('User', dbref=True)
    door = me.ReferenceField('Door', dbref=True)
    action = me.StringField(required=True)
    message = me.StringField(default='')
    details = me.DictField()
    log_date = me.DateTimeField(required=True,
                                     default=datetime.datetime.now)
    recorded_date = me.DateTimeField(required=True,
                                     default=datetime.datetime.now)

    meta = {'collection': 'history_logs'}
