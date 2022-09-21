from wtforms import Form, fields, validators
from pichayon import models
from flask_wtf import FlaskForm
from flask_mongoengine.wtf import model_form

BaseApplicationRemarkForm = model_form(
    models.Application,
    FlaskForm,
    only=["remark"],
    field_args={"remark": {"label": "Remark"}},
)


class ApplicationRemarkForm(BaseApplicationRemarkForm):
    pass
