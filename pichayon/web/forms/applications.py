from wtforms import Form, fields, validators
from pichayon import models

import datetime

from flask_wtf import FlaskForm
from wtforms import widgets
from flask_mongoengine.wtf import model_form

BaseApplicationForm = model_form(
    models.Application,
    FlaskForm,
    exclude=["users", "status", "created_date", "approved_date"],
    field_args={
        "degree": {"label": "Degrees"},
        "advisor": {
            "label": "Advisor",
            "label_modifier": lambda ad: f"{ad.first_name} {ad.last_name}",
        },
        "started_date": {"label": "Start Date", "format": "%Y-%m-%d %H:%M"},
        "ended_date": {"label": "End Date", "format": "%Y-%m-%d %H:%M"},
        "room": {"label": "Room", "label_modifier": lambda r: r.name},
        "purpose": {"label": "Purpose"},
        "request_checkbox": {"label": "ยอมรับนโยบายการเข้าใช้งานสถานที่"},
    },
)


class ApplicationForm(BaseApplicationForm):
    pass


BaseApplicationRemarkForm = model_form(
    models.Application,
    FlaskForm,
    only=["remark"],
    field_args={"remark": {"label": "Remark"}},
)


class ApplicationRemarkForm(BaseApplicationRemarkForm):
    pass


class UserGroupMemberFromApplicationForm(FlaskForm):
    user_groups = fields.SelectMultipleField(
        "User Group",
        validators=[validators.InputRequired()],
    )

    role = fields.SelectField(
        "Role",
        validators=[validators.InputRequired()],
        default="member",
        choices=[("member", "Member"), ("admin", "Admin")],
    )

    started_date = fields.DateTimeField(
        "Started Date",
        format="%Y-%m-%d %H:%M",
        default=datetime.date.today(),
        widget=widgets.TextInput(),
    )
    expired_date = fields.DateTimeField(
        "Expired Date",
        format="%Y-%m-%d %H:%M",
        validators=[validators.Optional()],
        widget=widgets.TextInput(),
    )
