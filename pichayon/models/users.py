import mongoengine as me
import datetime

from flask_login import UserMixin


class User(me.Document, UserMixin):
    username = me.StringField(required=True, unique=True)
    password = me.StringField()

    email = me.StringField()
    first_name = me.StringField(required=True)
    last_name = me.StringField(required=True)

    status = me.StringField(required=True, default='disactive')
    roles = me.ListField(me.StringField(), default=['user'])
    created_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.utcnow)
    updated_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.utcnow,
                                    auto_now=True)

    meta = {'collection': 'users'}

    def has_roles(self, roles):
        for role in roles:
            if role in self.roles:
                return True
        return False


class AuthCode(me.Document):
    user = me.ReferenceField(User, dbref=True)
    created_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.utcnow)
    expires_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.utcnow)

    meta = {'collection': 'auth_codes'}

    def is_expires(self):
        if self.expires_date < datetime.datetime.utcnow:
            return False
        return True
