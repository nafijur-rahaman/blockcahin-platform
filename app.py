import os
import logging
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from models import User  # make sure models.py has User
from extensions import db  # if you separate extensions, else use db directly

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
    # Import models to ensure tables are created
    import models
    db.create_all()

# Import and register blueprints
from auth import auth_bp
from dashboard import dashboard_bp
from admin import admin_bp
from payment import payment_bp

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(payment_bp)

# Landing page route
@app.route('/')
def landing():
    return render_template('landing.html')

# ===============================
# 🔹 One-Time Admin Creation Route
# ===============================
@app.route("/create-admin-temp")
def create_admin_temp():
    # Check if admin already exists
    if User.query.filter_by(is_admin=True).first():
        return "Admin already exists. This route is now disabled!"

    # Create first admin
    admin = User(email="admin@gmail.com")
    admin.set_password("123456")
    admin.is_admin = True

    db.session.add(admin)
    db.session.commit()

    # Optional: set a flag to prevent reuse (in memory)
    app.config['ADMIN_CREATED'] = True

    return "✅ Admin created! Login with admin@gmail.com / 123456. Route is now disabled."

# ===============================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)