__version__ = "0.0.1"


import optparse

from flask import Flask, request, abort, Response

from . import views
from . import acl
from . import oauth2
from .client import nats_client
from .client import pichayon_client
from .. import models


def create_app():
    app = Flask(__name__)
    app.config.from_object("pichayon.default_settings")
    app.config.from_envvar("PICHAYON_SETTINGS", silent=True)

    models.init_db(app)
    acl.init_acl(app)
    oauth2.init_oauth(app)

    views.register_blueprint(app)
    nats_client.nats_client.init_app(app)
    pichayon_client.init_client(nats_client.nats_client)
    return app


def get_program_options(default_host="127.0.0.1", default_port="8000"):

    """
    Takes a flask.Flask instance and runs it. Parses
    command-line flags to configure the app.
    """

    # Set up the command-line options
    parser = optparse.OptionParser()
    parser.add_option(
        "-H",
        "--host",
        help="Hostname of the Flask app " + "[default %s]" % default_host,
        default=default_host,
    )
    parser.add_option(
        "-P",
        "--port",
        help="Port for the Flask app " + "[default %s]" % default_port,
        default=default_port,
    )

    # Two options useful for debugging purposes, but
    # a bit dangerous so not exposed in the help message.
    parser.add_option(
        "-c", "--config", dest="config", help=optparse.SUPPRESS_HELP, default=None
    )
    parser.add_option(
        "-d", "--debug", action="store_true", dest="debug", help=optparse.SUPPRESS_HELP
    )
    parser.add_option(
        "-p",
        "--profile",
        action="store_true",
        dest="profile",
        help=optparse.SUPPRESS_HELP,
    )

    options, _ = parser.parse_args()

    # If the user selects the profiling option, then we need
    # to do a little extra setup
    if options.profile:
        from werkzeug.contrib.profiler import ProfilerMiddleware

        app.config["PROFILE"] = True
        app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])
        options.debug = True

    return options
