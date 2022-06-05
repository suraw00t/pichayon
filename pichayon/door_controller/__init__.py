from .server import DoorControllerServer


def create_server():
    from pichayon.utils import config

    settings = config.get_settings()
    server = DoorControllerServer(settings)
    return server
