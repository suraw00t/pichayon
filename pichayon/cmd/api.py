from pichayon.utils import program_options
from pichayon import api


def main():
    options = program_options.get_program_options(default_port=8000)

    app = api.create_app()

    program_options.initial_profile(app, options)

    app.run(debug=options.debug, host=options.host, port=int(options.port))
