import mongoengine as me
import datetime

from flask_login import UserMixin

ROLE_CHOICES = [
    ("admin", "Admin"),
    ("lecturer", "Lecturer"),
    ("supervisor", "Supervisor"),
    ("student", "Student"),
    ("user", "User"),
]


class Identity(me.EmbeddedDocument):
    identifier = me.StringField(required=True, default="")
    type = me.StringField(required=True, default="rfid")
    status = me.StringField(default=True, status="active")
    added_with = me.StringField(required=True, default="web")
    added_by = me.StringField(required=True, default="system")

    created_date = me.DateTimeField(required=True, default=datetime.datetime.now())
    updated_date = me.DateTimeField(required=True, default=datetime.datetime.now())


class User(me.Document, UserMixin):
    username = me.StringField(required=True, unique=True, max_length=256)
    email = me.StringField(max_length=256)
    first_name = me.StringField(required=True, max_length=256)
    last_name = me.StringField(required=True, max_length=256)

    first_name_th = me.StringField(required=True, default="", max_length=256)
    last_name_th = me.StringField(required=True, default="", max_length=256)

    system_id = me.StringField(default="", required=True, max_length=256)

    id_card_number = me.StringField(default="", max_length=13)

    identities = me.EmbeddedDocumentListField(Identity)

    gave_informations = me.BooleanField(
        required=True,
        default=False,
    )

    profile_image = me.FileField()

    status = me.StringField(required=True, default="active", max_length=100)

    roles = me.ListField(me.StringField(), default=["user"])

    created_date = me.DateTimeField(
        required=True,
        default=datetime.datetime.now,
    )
    updated_date = me.DateTimeField(
        required=True,
        default=datetime.datetime.now,
        auto_now=True,
    )

    resources = me.DictField()

    meta = {"collection": "users"}

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def has_roles(self, *roles):
        for role in roles:
            if role in self.roles:
                return True
        return False

    def get_image(self):
        if "google" in self.resources:
            return self.resources["google"].get("picture", None)
        return None

    def get_user_groups(self):
        from .groups import UserGroupMember

        user_group_members = UserGroupMember.objects(user=self)
        user_groups = [ugm.group for ugm in user_group_members]
        return user_groups
