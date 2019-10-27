from browser import document, ajax, bind


@bind("div.opendoor", "click")
def open_door(ev):
    # print(ev.target.id)
    door_id = ev.target.id
    # ajax.post(f'/cameras/{camera_id}/stoplpr',
              # data={'project_id': project_id})
    print(door_id)

