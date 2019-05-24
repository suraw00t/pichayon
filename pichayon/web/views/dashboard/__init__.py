from flask import Blueprint, render_template
from flask_login import login_required

module = Blueprint('web.dashboard', __name__, url_prefix='/dashboard')


@module.route('/')
@login_required
def index():
    return render_template('/dashboard/index.html')
