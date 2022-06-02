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
            self.topic = self.sparkbit_topic

        return self.topic

    def open_door(self, door, user, type="pichayon"):
        data = {
            "action": "open",
            "door_id": str(door.id),
            "device_type": door.device_type,
            "user_id": str(user.id),
        }
        topic = self.get_topic(type)
        return self.message_client.publish(topic, data)

    def get_door_state(self, door, type="pichayon"):
        data = {
            "action": "state",
            "door": {"id": str(door.id), "state": "unknow"},
        }

        topic = self.get_topic(type)
        return self.message_client.request(topic, data)

    def change_door_group(self, door_group):
        data = {
            "action": "change_door_group",
            "door_group_id": str(door_group.id),
        }

        topic = self.get_topic()
        return self.message_client.request(topic, data)

    def change_user_group(self, user_group):
        data = {
            "action": "change_user_group",
            "user_group_id": str(user_group.id),
        }

        topic = self.get_topic()
        return self.message_client.request(topic, data)

    def update_member(self, user):

        data = {
            "action": "update-member",
            "user_id": str(user.id),
        }

        topic = self.get_topic()
        return self.message_client.request(topic, data)

    def change_authorization(self, authorization):
        data = {
            "action": "change_authorization",
            "authorization_id": str(authorization.id),
        }

        topic = self.get_topic()
        return self.message_client.request(topic, data)


pichayon_client = PichayonClient()


def init_client(message_client):
    pichayon_client.init_app(message_client)
