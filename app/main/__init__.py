from flask import Blueprint

# Initialise blueprints
bp = Blueprint('main', __name__)

# Import routes
# Since PEP8 dislikes mid file imports, warning has been supressed
# TODO: Consider a means of importing routes without breaking PEP8
from app.main import routes  # nopep8
