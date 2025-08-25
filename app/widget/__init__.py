"""
Sanctum Chat Widget Blueprint

This blueprint provides embeddable chat widget functionality
that can be integrated into any website or application.
"""

from flask import Blueprint

bp = Blueprint('widget', __name__,
               url_prefix='/widget',
               static_folder='static',
               template_folder='templates')

from . import routes
