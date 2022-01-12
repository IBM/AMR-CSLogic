"""
Package: service
Package for the application models and service routes
This module creates and configures the Flask app and sets up the logging
"""
import importlib
import logging
import os

from flask import Flask

# Create Flask application
app = Flask(__name__)
app.config.from_object("config")

# Import the routes After the Flask app is created
user_module_name = os.path.split(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))[1]
submodule_name = os.path.split(os.path.abspath(os.path.dirname(__file__)))[1]
for file in os.listdir(os.path.dirname(__file__)):
    if file.endswith('.py') and not file.startswith('_'):
        module = file[:file.find('.py')]
        importlib.import_module(user_module_name + '.' + submodule_name + '.' + module)

# Set up logging for production
print("Setting up logging for {}...".format(__name__))
app.logger.propagate = False
if __name__ != "__main__":
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
    # Make all log formats consistent
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(module)s] %(message)s", "%Y-%m-%d %H:%M:%S %z"
    )
    for handler in app.logger.handlers:
        handler.setFormatter(formatter)
    app.logger.info("Logging handler established")

app.logger.info(70 * "*")
app.logger.info("  A M R   V E R B N E T   S E R V I C E  ".center(70, "*"))
app.logger.info(70 * "*")

app.logger.info("Service inititalized!")

