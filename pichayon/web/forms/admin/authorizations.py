from wtforms import Form
from wtforms import fields
from wtforms import validators
from wtforms.fields import html5
import datetime
from flask_wtf import FlaskForm


class AddAuthorityForm(FlaskForm):
    user_group = fields.SelectMultipleField('User Group')
    started_date = fields.DateTimeField('Start Date',
                                        format='%Y-%m-%d %H:%M',
                                        default=datetime.datetime.now()
                                        )
    expired_date = fields.DateTimeField('Expire Date',
                                        format='%Y-%m-%d %H:%M',
                                        default=datetime.datetime.now()
                                        )
