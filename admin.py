from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import User, GoogleAdsAccount, Transaction, UserGoogleAdsAccount
from app import db
from auth import admin_required
from forms import AdminAccountForm, AdminUserForm
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    # Get statistics
    total_users = User.query.count()
    total_funds = db.session.query(func.sum(Transaction.amount)).scalar() or 0
    total_fees = db.session.query(func.sum(Transaction.fee)).scalar() or 0
    total_ads_accounts = GoogleAdsAccount.query.count()
    assigned_accounts = GoogleAdsAccount.query.filter_by(is_assigned=True).count()
    
    # Recent transactions
    recent_transactions = Transaction.query.order_by(Transaction.created_at.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_funds=total_funds,
                         total_fees=total_fees,
                         total_ads_accounts=total_ads_accounts,
                         assigned_accounts=assigned_accounts,
                         recent_transactions=recent_transactions)

@admin_bp.route('/users')
@admin_required
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=all_users)

@admin_bp.route('/accounts')
@admin_required
def accounts():
    form = AdminAccountForm()
    all_accounts = GoogleAdsAccount.query.order_by(GoogleAdsAccount.created_at.desc()).all()
    return render_template('admin/accounts.html', accounts=all_accounts, form=form)

@admin_bp.route('/add-account', methods=['POST'])
@admin_required
def add_account():
    form = AdminAccountForm()
    
    if form.validate_on_submit():
        # Check if account ID already exists
        existing = GoogleAdsAccount.query.filter_by(account_id=form.account_id.data).first()
        if existing:
            flash('Account ID already exists.', 'danger')
        else:
            account = GoogleAdsAccount(
                account_id=form.account_id.data,
                account_name=form.account_name.data
            )
            db.session.add(account)
            db.session.commit()
            flash('Google Ads account added successfully.', 'success')
    else:
        flash('Invalid form data.', 'danger')
    
    return redirect(url_for('admin.accounts'))

@admin_bp.route('/remove-account/<int:account_id>', methods=['POST'])
@admin_required
def remove_account(account_id):
    account = GoogleAdsAccount.query.get_or_404(account_id)
    
    # Check if account is assigned to any user
    if account.is_assigned:
        flash('Cannot remove assigned account. Unassign first.', 'danger')
    else:
        db.session.delete(account)
        db.session.commit()
        flash('Account removed successfully.', 'success')
    
    return redirect(url_for('admin.accounts'))

@admin_bp.route('/toggle-user-admin/<int:user_id>', methods=['POST'])
@admin_required
def toggle_user_admin(user_id):
    user = User.query.get_or_404(user_id)
    
    # Prevent removing admin status from the current admin
    if user.id == session['user_id'] and user.is_admin:
        flash('Cannot remove your own admin status.', 'danger')
    else:
        user.is_admin = not user.is_admin
        db.session.commit()
        status = 'Admin' if user.is_admin else 'User'
        flash(f'{user.email} is now a {status}.', 'success')
    
    return redirect(url_for('admin.users'))

@admin_bp.route('/transactions')
@admin_required
def transactions():
    all_transactions = Transaction.query.order_by(Transaction.created_at.desc()).all()
    return render_template('admin/transactions.html', transactions=all_transactions)
