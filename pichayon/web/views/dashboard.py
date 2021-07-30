from flask import (Blueprint,
                   render_template,
                   url_for,
                   request,
                   Response,
                   redirect,
                   g)
from flask_login import login_required, current_user
from pichayon import models
import json
import datetime

module = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@module.route('/')
@login_required
def index():
    if not current_user.gave_informations:
        return redirect(url_for('accounts.edit_profile'))

    # door_auths = models.DoorAuthorization.objects()
    # groups = models.UserGroup.objects()
    # door_groups = list()
    # cu_groups = list()
    # user_group = dict()
    # for group in groups:
    #     if group.is_user_member(current_user._get_current_object()):
    #         cu_groups.append(group)

    # for door_auth in door_auths:
    #     for group in cu_groups:
    #         if not door_auth.is_authority(group):
    #             continue
    #         door_groups.append(door_auth.door_group)
    #         user_group[door_auth.door_group.id] = group
    door_groups = []
    user_group = []
    return render_template('/dashboard/index.html',
                           door_groups=door_groups,
                           user_group=user_group)


@module.route('/open_door', methods=('GET', 'POST'))
@login_required
def open_door():
    door_id = request.form.get('door_id')
    user_group_id = request.form.get('user_group_id')
    door = models.Door.objects.get(id=door_id)
    # print(door_id)
    loop = g.get_loop()
    data = json.dumps({
            'action': 'open',
            'door_id': door_id,
            'type': door.type,
            'user_group_id': user_group_id,
            'user_id': str(current_user._get_current_object().id)
        })
    nats_client = g.get_nats_client()
    loop.run_until_complete(nats_client.publish(
        'pichayon.controller.command',
        data.encode()
        ))
    response = Response()
    response.status_code = 200
    history_log = models.HistoryLog(
            action = 'open',
            message = f'{current_user._get_current_object().username} opened Door: {door.name} via Web Application',
            details = {
                'door': str(door.id),
                'user': str(current_user._get_current_object().username)
                },
            recorded_date = datetime.datetime.now()
            )
    history_log.save()
    return response

