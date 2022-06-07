from browser import document, ajax, bind


@bind("div.opendoor", "click")
def open_door(ev):
    # print(ev.target.id)
    door_id = ev.target.id
    ajax.post(f"/dashboard/open_door", data={"door_id": door_id})
    print("open_door")
