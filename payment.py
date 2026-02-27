from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import Transaction, User
from app import db
from auth import login_required
from forms import PaymentForm

payment_bp = Blueprint('payment', __name__, url_prefix='/payment')

@payment_bp.route('/add-funds', methods=['GET', 'POST'])
@login_required
def add_funds():
    form = PaymentForm()
    platform = request.args.get('platform', 'google')
    
    if form.validate_on_submit():
        user = User.query.get(session['user_id'])
        amount = form.amount.data
        
        # Create a new transaction
        transaction = Transaction(
            user_id=user.id,
            amount=amount,
            fee=0.0  # Assuming 0 fee for now, adjust as needed
        )
        db.session.add(transaction)
        db.session.commit()
        
        flash(f'Successfully added ${amount} via {platform}.', 'success')
        return redirect(url_for('dashboard.dashboard'))
        
    return render_template('payment.html', form=form, platform=platform)