"""
WSGI entry point for Gunicorn to use with the HomeFinder application.
This file provides a standardized way for WSGI servers to interact with the Flask application.
"""

# Import the Flask application instance
from web_app import app

# This is the object that Gunicorn will use
application = app

# For compatibility with different WSGI servers
if __name__ == "__main__":
    app.run()
