from wtforms import Form
from wtforms import fields
from wtforms import validators
from wtforms import widgets
from flask_wtf import FlaskForm
from flask_mongoengine.wtf import model_form
from io import StringIO

from pichayon import models
from ..fields import TagListField


class MultiCheckboxField(fields.SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    # widget = MultiCheckboxField()
    option_widget = widgets.CheckboxInput()


class AddingUserForm(FlaskForm):
    username = fields.SelectMultipleField("Username")


class AddRoleUserForm(FlaskForm):
    role = fields.SelectMultipleField("Role")


# class UserForm(FlaskForm):
#     username = fields.StringField(
#         "Username", validators=[validators.InputRequired(), validators.Length(min=3)]
#     )
# rooms = MultiCheckboxField('Rooms')

BaseUserForm = model_form(
    models.User,
    FlaskForm,
    exclude=[
        "created_date",
        "updated_date",
        "last_login_date",
        "roles",
        "resources",
        "identities",
        "gave_informations",
    ],
    field_args={
        "first_name": {"label": "First Name"},
        "last_name": {"label": "Last Name"},
        "first_name_th": {"label": "Thai First Name"},
        "last_name_th": {"label": "Thai Last Name"},
        "system_id": {"label": "Systen ID"},
        "email": {"label": "Email"},
        "username": {"label": "Username"},
        "status": {"label": "Status"},
        "id_card_number": {"label": "Citizen ID"},
    },
)


class UserForm(BaseUserForm):
    roles = TagListField("Roles", default=["user"])


class AddingRoomForm(FlaskForm):
    room = fields.SelectField("Rooms")
    started_date = fields.DateField("Started Date", format="%Y-%m-%d")
    expired_date = fields.DateField("Expired Date", format="%Y-%m-%d")


class IdentityForm(FlaskForm):
    identifier = fields.StringField(
        "ID",
        validators=[validators.InputRequired()],
    )
    type = fields.SelectField("Type", choices=[("rfid", "RFID")], default="rfid")
    status = fields.SelectField(
        "Status",
        choices=[("active", "Active"), ("disactive", "Disactive")],
        default="active",
    )


class EditForm(FlaskForm):
    roles = fields.SelectMultipleField("Role")
    system_id = fields.StringField("System ID")
