from flask import (Blueprint,
                   render_template,
                   url_for,
                   redirect)
from flask_login import login_required, current_user

module = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@module.route('/')
@login_required
def index():
    if not current_user.gave_informations:
        return redirect(url_for('accounts.edit_profile'))
    return render_template('/dashboard/index.html')
