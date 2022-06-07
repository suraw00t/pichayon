from wtforms import Form
from wtforms import fields
from wtforms import validators
from wtforms import widgets
from flask_wtf import FlaskForm
from io import StringIO


class MultiCheckboxField(fields.SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    # widget = MultiCheckboxField()
    option_widget = widgets.CheckboxInput()


class AddingUserForm(FlaskForm):
    username = fields.SelectMultipleField("Username")


class AddRoleUserForm(FlaskForm):
    role = fields.SelectMultipleField("Role")


class UserForm(FlaskForm):
    username = fields.StringField(
        "Username", validators=[validators.InputRequired(), validators.Length(min=3)]
    )
    # rooms = MultiCheckboxField('Rooms')


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
