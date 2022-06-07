from pichayon import door_controller


def main():
    server = door_controller.create_server()
    server.run()
