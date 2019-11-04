from flask import (Blueprint,
                   render_template,
                   url_for,
                   redirect)
from flask_login import login_required, current_user
from pichayon import models
module = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@module.route('/')
@login_required
def index():
    if not current_user.gave_informations:
        return redirect(url_for('accounts.edit_profile'))

    door_auths = models.DoorAuthorizations.objects()
    groups = models.UserGroup.objects()
    door_groups = list()
    cu_groups = list()
    for group in groups:
        if group.is_member(current_user._get_current_object()):
            cu_groups.append(group)

    for door_auth in door_auths:
        for group in cu_groups:
            if door_auth.is_expired(group):
                continue
            door_groups.append(door_auth.door_group)

    return render_template('/dashboard/index.html',
                           door_groups=door_groups)
