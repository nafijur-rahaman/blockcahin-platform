from flask import Blueprint, render_template, session, redirect, url_for, flash
from models import User, Transaction, UserGoogleAdsAccount
from auth import login_required

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('auth.login'))
    
    # Get recent transactions
    recent_transactions = Transaction.query.filter_by(user_id=user.id)\
                                         .order_by(Transaction.created_at.desc())\
                                         .limit(10).all()
    
    # Get assigned Google Ads accounts
    assigned_accounts = UserGoogleAdsAccount.query.filter_by(user_id=user.id)\
                                                  .order_by(UserGoogleAdsAccount.assigned_at.desc())\
                                                  .all()
    
    # Calculate total ad credit
    total_ad_credit = user.get_total_ad_credit()
    
    return render_template('dashboard.html', 
                         user=user, 
                         recent_transactions=recent_transactions,
                         assigned_accounts=assigned_accounts,
                         total_ad_credit=total_ad_credit)

@dashboard_bp.route('/transactions')
@login_required
def transactions():
    user = User.query.get(session['user_id'])
    all_transactions = Transaction.query.filter_by(user_id=user.id)\
                                       .order_by(Transaction.created_at.desc())\
                                       .all()
    
    return render_template('transactions.html', 
                         user=user, 
                         transactions=all_transactions)
