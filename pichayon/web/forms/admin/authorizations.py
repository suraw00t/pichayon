from wtforms import Form
from wtforms import fields
from wtforms import validators
import datetime
from flask_wtf import FlaskForm

DAYS = ['Monday', 'Tuesday', 'Wednesday',
        'Thursday', 'Friday', 'Saturday', 'Sunday']


class AddAuthorityForm(FlaskForm):
    user_group = fields.SelectField('User Group')
    started_date = fields.DateTimeField('Start Date',
                                        format='%Y-%m-%d %H:%M',
                                        default=datetime.datetime.now()
                                        )
    expired_date = fields.DateTimeField('Expire Date',
                                        format='%Y-%m-%d %H:%M',
                                        default=datetime.datetime.now()
                                        )
    days = fields.SelectMultipleField('Select Days',
                                      choices=[(str(i), day) for i, day in enumerate(DAYS)])
    start_time = fields.TimeField('Start Time')
    end_time = fields.TimeField('End Time')
