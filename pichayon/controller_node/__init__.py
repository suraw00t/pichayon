from .server import ControllerNodeServer

def create_server():
    from pichayon.utils import config
    settings = config.get_settings()
    server = ControllerNodeServer(settings)
    return server
