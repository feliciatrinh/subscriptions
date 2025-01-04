from flask import flash, render_template, redirect, request, url_for
from application import app, db
from application.forms import EditSubscriptionForm, LogForm, SubscriptionForm
from application.models import Log, Media, Subscription, PaymentFrequency

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Lisha'}
    subs = Subscription.get(orderby=Subscription.monthly_cost.desc(), filterby=Subscription.inactive_date.is_(None))
    total_monthly_cost = f'${Subscription.total_monthly_cost():.2f}'
    total_yearly_cost = f'${Subscription.total_yearly_cost():.2f}'
    content = {
        "title": "Home",
        "user": user,
        "subscriptions": subs,
        "total_monthly_cost": total_monthly_cost,
        "total_yearly_cost": total_yearly_cost
    }
    return render_template('index.html', **content)


@app.route('/subscription', methods=['GET', 'POST'])
def subscription():
    form = SubscriptionForm()
    if form.validate_on_submit():
        sub = Subscription(
            name=form.name.data,
            cost=f'{form.cost.data:.2f}',
            payment_frequency=form.payment_frequency.data,
            active_date=form.active_date.data
        )
        db.session.add(sub)
        db.session.commit()
        flash('Subscription was added')
        return redirect(url_for('index'))
    return render_template('subscriptionform.html', title='Subscription', form=form)


@app.route('/subscription/update', methods=['GET', 'POST'])
def subscription_update():
    form = EditSubscriptionForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            existing_sub = db.session.get(Subscription, form.subscription.data)
            if form.cost.data:
                existing_sub.cost = f'{form.cost.data:.2f}'
            if form.payment_frequency.data != PaymentFrequency.no_change:
                existing_sub.payment_frequency = form.payment_frequency.data
            if form.active_date.data:
                existing_sub.active_date = form.active_date.data
            if form.inactive_date.data:
                existing_sub.inactive_date = form.inactive_date.data
            db.session.commit()
            flash('Subscription was updated')

            return redirect(url_for('index'))
        return render_template('subscriptionupdate.html', title='Update Subscription', form=form)
    else:
        return render_template('subscriptionupdate.html', title='Update Subscription', form=form)


def get_or_create_media_id(title, media_type):
    title = title.strip()
    existing_media = Media.get_by_title_type(title, media_type)
    if existing_media:
        media_id = existing_media.id
    else:
        media = Media(title=title, type=media_type)
        db.session.add(media)
        db.session.commit()
        media_id = media.id
    return media_id


@app.route('/log', methods=['GET', 'POST'])
def log():
    form = LogForm()
    if form.validate_on_submit():
        media_id = get_or_create_media_id(form.media_title.data, form.media_type.data)
        to_log = Log(
            date=form.date.data,
            subscription_id=form.subscription.data,
            media_id=media_id,
            season=form.season_number.data,
            episode=form.episode_number.data,
            notes=form.notes.data
        )
        db.session.add(to_log)
        db.session.commit()
        flash('Log was submitted')
        return redirect(url_for('index'))
    return render_template('logform.html', title='Log', form=form)
