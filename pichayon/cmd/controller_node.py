from pichayon import controller_node


def main():
    server = controller_node.create_server()
    server.run()

