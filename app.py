from config import app
from models import db
from controllers import *

# Initialize the database
db.init_app(app)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)