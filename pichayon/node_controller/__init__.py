from .server import NodeControllerServer

def create_server():
    from pichayon.utils import config
    settings = config.get_settings()
    server = NodeControllerServer(settings)
    return server
