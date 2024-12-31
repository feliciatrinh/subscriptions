from decimal import Decimal
from flask import render_template, flash, redirect, url_for
import sqlalchemy as sa
from application import app, db
from application.forms import SubscriptionForm
from application.models import Subscription

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Lisha'}
    subs = db.session.scalars(sa.select(Subscription)).all()
    return render_template('index.html', title='Home', user=user, subscriptions=subs)


@app.route('/subscription', methods=['GET', 'POST'])
def subscription():
    form = SubscriptionForm()
    if form.validate_on_submit():
        sub = Subscription(
            name=form.name.data,
            cost=Decimal(form.cost.data).quantize(Decimal('0.00')),
            payment_frequency=form.payment_frequency.data,
            active_date=form.active_date.data
        )
        db.session.add(sub)
        db.session.commit()
        flash('Subscription was added')
        return redirect(url_for('index'))
    return render_template('subscriptionform.html', title='Subscription', form=form)
