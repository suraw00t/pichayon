import os
import flask

settings = None


def get_settings():
    global settings

    if not settings:
        filename = os.environ.get('PICHAYON_SETTINGS', None)

        if filename is None:
            print('This program require PICHAYON_SETTINGS environment')
            return
        print(filename)

        file_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), '../../')

        settings = flask.config.Config(file_path)
        settings.from_object('pichayon.default_settings')
        settings.from_envvar('PICHAYON_SETTINGS', silent=True)

    return settings

