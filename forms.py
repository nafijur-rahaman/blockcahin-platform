from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FloatField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, Length, NumberRange, ValidationError
from models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email.')

class PaymentForm(FlaskForm):
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=500, max=10000)])

class AdminAccountForm(FlaskForm):
    account_id = StringField('Account ID', validators=[DataRequired(), Length(min=10, max=20)])
    account_name = StringField('Account Name', validators=[DataRequired(), Length(min=1, max=100)])

class AdminUserForm(FlaskForm):
    user_id = SelectField('User', coerce=int, validators=[DataRequired()])
    is_admin = BooleanField('Admin Status')
