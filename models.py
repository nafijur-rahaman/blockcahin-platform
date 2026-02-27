from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships to link this user to their transactions and ad accounts
    transactions = db.relationship('Transaction', backref='user', lazy=True)
    assigned_accounts = db.relationship('UserGoogleAdsAccount', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def get_total_ad_credit(self):
        # Calculates total credit based on transactions (amount minus fees)
        total = 0
        for tx in self.transactions:
            total += (tx.amount - tx.fee)
        return total

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    fee = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class GoogleAdsAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.String(20), unique=True, nullable=False)
    account_name = db.Column(db.String(100), nullable=False)
    is_assigned = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to track who this account is assigned to
    assignments = db.relationship('UserGoogleAdsAccount', backref='google_account', lazy=True)

class UserGoogleAdsAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('google_ads_account.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)