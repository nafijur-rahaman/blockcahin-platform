import os
import logging
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///local.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

with app.app_context():
    # Late import of models to avoid circular import
    import models
    db.create_all()

# Import and register blueprints AFTER db & models are ready
from auth import auth_bp
from dashboard import dashboard_bp
from admin import admin_bp
try:
    from payment import payment_bp
    app.register_blueprint(payment_bp)
except ModuleNotFoundError:
    # If payment.py doesn't exist, skip it for now
    print("payment_bp not found, skipping")

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(admin_bp)

# Landing page route
@app.route('/')
def landing():
    return render_template('landing.html')

# One-time admin creation route
@app.route("/create-admin-temp")
def create_admin_temp():
    from models import User  # late import to avoid circular
    if User.query.filter_by(is_admin=True).first():
        return "Admin already exists. Route disabled!"

    admin = User(email="admin1@gmail.com")
    admin.set_password("123456")
    admin.is_admin = True

    db.session.add(admin)
    db.session.commit()
    return "✅ Admin created! Login with admin@gmail.com / 123456"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)