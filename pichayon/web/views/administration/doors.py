from flask import (Blueprint,
                   render_template,
                   redirect,
                   url_for,
                   request,
                   g)

from pichayon import models
from pichayon.web import acl
from pichayon.web.forms.admin import DoorForm, DoorGroupForm
from flask_login import login_user, logout_user, login_required, current_user
import string
import random
import json

module = Blueprint('administration.doors',
                   __name__,
                   url_prefix='/doors')


def generate_passcode():
    res = ''.join(random.choices('ABCD' +
                                 string.digits, k=6))
    print('pass>>>>', res)
    return str(res)


@module.route('/')
@acl.allows.requires(acl.is_admin)
def index():
    door_groups = models.DoorGroup.objects(status='active').order_by('name')
    return render_template('/administration/doors/index.html',
                           door_groups=door_groups)


@module.route('/create', methods=["GET", "POST"])
@acl.allows.requires(acl.is_admin)
def create():
    form = DoorForm()
    form.type.choices = [('pichayon', 'Pichayon'), ('sparkbit', 'Sparkbit')]
    group_id = request.args.get('group_id')
    door_group = models.DoorGroup.objects.get(id=group_id)
    if models.Door.objects(device_id=form.device_id.data).first():
        return render_template('/administration/doors/create-edit.html',
                               form=form,
                               door_group=door_group,
                               device_id_error="True")
    if not form.validate_on_submit():
        return render_template('/administration/doors/create-edit.html',
                               form=form,
                               door_group=door_group)
    door = models.Door()
    form.populate_obj(door)
    door.creator = current_user._get_current_object()
    if form.have_passcode.data:
        door.passcode = generate_passcode()
    door.save()
    
    if form.type.data == 'sparkbit':
        sparkbit_system = models.SparkbitDoorSystem()
        form.populate_obj(sparkbit_system)
        sparkbit_system.door = door
        sparkbit_system.name = f'{door_group.name}-{form.name.data}'
        sparkbit_system.status = 'active'
        sparkbit_system.creator = current_user._get_current_object()
        sparkbit_system.save()
    
    door_group.members.append(door)
    door_group.save()
    return redirect(url_for('administration.doors.doors_list',
                            doorgroup_id=group_id))


@module.route('/<doorgroup_id>/doors_list', methods=["GET", "POST"])
@acl.allows.requires(acl.is_admin)
def doors_list(doorgroup_id):
    door_group = models.DoorGroup.objects.get(id=doorgroup_id)
    return render_template('/administration/doors/door_lists.html',
                           door_group=door_group)


@module.route('/<door_id>/edit', methods=["GET", "POST"])
@acl.allows.requires(acl.is_admin)
def edit(door_id):
    group_id = request.args.get('group_id')
    door_group = models.DoorGroup.objects.get(id=group_id)
    door = models.Door.objects.get(id=door_id)

    form = DoorForm(obj=door)
    form.type.choices = [('pichayon', 'Pichayon'), ('sparkbit', 'Sparkbit')]

    if not form.validate_on_submit():
        if len(door.passcode) == 6:
            form.have_passcode.data = True
        return render_template('/administration/doors/create-edit.html',
                               form=form,
                               door_group=door_group)

    if door.device_id == form.device_id.data:
        form.populate_obj(door)
        if len(door.passcode) == 6:
            if not form.have_passcode.data:
                door.passcode = ''
        elif form.have_passcode.data:
            door.passcode = generate_passcode()
        door.save()
        return redirect(url_for('administration.doors.doors_list',
                                doorgroup_id=group_id))

    if models.Door.objects(device_id=form.device_id.data).first():
        return render_template('/administration/doors/create-edit.html',
                               form=form,
                               door_group=door_group,
                               device_id_error="True")
    form.populate_obj(door)
    if len(door.passcode) == 6:
        if not form.have_passcode.data:
            door.passcode = ''
    elif form.have_passcode.data:
        door.passcode = generate_passcode()
    door.save()
    if form.type.data == 'sparkbit':
        sparkbit_system = models.SparkbitDoorSystem.objects(door=door).first()
        form.populate_obj(sparkbit_system)
        sparkbit_system.name = f'{door_group.name}-{form.name.data}'
        sparkbit_system.status = 'active'
        sparkbit_system.creator = current_user._get_current_object()
        sparkbit_system.save()

    return redirect(url_for('administration.doors.doors_list',
                            doorgroup_id=group_id))


@module.route('/<door_id>/delete')
@acl.allows.requires(acl.is_admin)
def delete(door_id):
    group_id = request.args.get('group_id')
    door_group = models.DoorGroup.objects.get(id=group_id)
    selected_door = models.Door.objects.get(id=door_id)
    if selected_door.type == 'sparkbit':
        sparkbit_system = models.SparkbitDoorSystem.objects(door=selected_door).first()
        if sparkbit_system:
            sparkbit_system.delete()
    door_group.members.remove(selected_door)
    selected_door.delete()
    door_group.save()
    return redirect(url_for('administration.doors.doors_list',
                            doorgroup_id=group_id))


@module.route('/<door_id>/revoke_passcode')
@acl.allows.requires(acl.is_admin)
def revoke_passcode(door_id):
    door = models.Door.objects.get(id=door_id)
    door.passcode = generate_passcode()
    door.save()
    loop = g.get_loop()
    data = json.dumps({
        'action': 'update_passcode',
        'door_id': door_id
        })
    nats_client = g.get_nats_client()
    loop.run_until_complete(nats_client.publish(
        'pichayon.controller.command',
        data.encode()
        ))
    return redirect(url_for('dashboard.index'))
