import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set the database path explicitly
basedir = os.path.abspath(os.path.dirname(__file__))
app_dir = os.path.join(basedir, 'app')
db_path = os.path.join(app_dir, 'medml.db')
os.environ['DATABASE_URL'] = f'sqlite:///{os.path.abspath(db_path).replace(chr(92), "/")}'

from app import create_app

# Get the config name from environment or use 'default'
config_name = os.getenv('FLASK_ENV', 'default')
app = create_app(config_name)

if __name__ == '__main__':
    app.run(debug=True)