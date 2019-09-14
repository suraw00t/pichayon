from wtforms import Form
from wtforms import fields
from wtforms import validators
from wtforms.fields import html5
from wtforms import widgets
from flask_wtf import FlaskForm
from io import StringIO


class MultiCheckboxField(fields.SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    # widget = MultiCheckboxField()
    option_widget = widgets.CheckboxInput()


class AddingUserForm(FlaskForm):
    username = fields.SelectMultipleField('Username')


class AddRoleUserForm(FlaskForm):
    role = fields.SelectField('Role')


class UserForm(FlaskForm):
    username = fields.TextField(
            'Username',
            validators=[validators.InputRequired(),
                        validators.Length(min=3)])
    # rooms = MultiCheckboxField('Rooms')


class AddingRoomForm(FlaskForm):
    room = fields.SelectField('Rooms')
    started_date = html5.DateField('Started Date',
                                    format='%Y-%m-%d')
    expired_date = html5.DateField('Expired Date',
                                    format='%Y-%m-%d')
