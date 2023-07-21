class PichayonClient:
    def __init__(self, message_client=None):
        self.message_client = message_client
        self.topic = "pichayon.controller.command"
        self.sparkbit_topic = "pichayon.controller.sparkbit.command"

    def init_app(self, message_client=None):
        self.message_client = message_client

    def get_topic(self, type="pichayon"):
        topic = self.topic
        if type == "sparkbit":
            topic = self.sparkbit_topic

        return topic

    def open_door(self, door, user, type="pichayon", ip="127.0.0.1"):
        data = {
            "action": "open-door",
            "door_id": str(door.id),
            "device_type": door.device_type,
            "user_id": str(user.id),
            "ip": ip,
        }

        return self.message_client.publish(self.topic, data)

    def get_door_state(self, door, type="pichayon"):
        data = {
            "action": "get-door-state",
            "door": {"id": str(door.id), "state": "unknow"},
        }

        topic = self.get_topic(type)
        return self.message_client.request(topic, data)

    # def change_door_group(self, door_group):
    #     data = {
    #         "action": "change-door-group",
    #         "door_group_id": str(door_group.id),
    #     }

    #     return self.message_client.request(self.topic, data)

    # def change_user_group(self, user_group):
    #     data = {
    #         "action": "change-user-group",
    #         "user_group_id": str(user_group.id),
    #     }

    #     return self.message_client.request(self.topic, data)
    def update_door_information(self, door, user, ip):
        data = {
            "action": "update-door-information",
            "user_id": str(user.id),
            "door_id": str(door.id),
            "ip": ip,
        }

        topic = self.get_topic()
        return self.message_client.publish(topic, data)

    def update_member(self, user):
        data = {
            "action": "update-member",
            "user_id": str(user.id),
        }

        topic = self.get_topic()
        return self.message_client.publish(topic, data)

    def update_authorization(self, authorization, user, ip):
        data = {
            "action": "update-authorization",
            "authorization_id": str(authorization.id),
            "ip": ip,
            "user": str(user.id),
        }

        return self.message_client.publish(self.topic, data)

    def delete_authorization(self, authorization, user, ip):
        data = {
            "action": "delete-authorization",
            "authorization_id": str(authorization.id),
            "ip": ip,
            "user": str(user.id),
        }

        return self.message_client.publish(self.topic, data)


pichayon_client = PichayonClient()


def init_client(message_client):
    pichayon_client.init_app(message_client)
