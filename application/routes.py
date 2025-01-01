from flask import render_template, flash, redirect, url_for
import sqlalchemy as sa
from sqlalchemy import func as f
from application import app, db
from application.forms import LogForm, SubscriptionForm
from application.models import Log, Media, Subscription

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
            cost=f'{form.cost.data:.2f}',
            payment_frequency=form.payment_frequency.data,
            active_date=form.active_date.data
        )
        db.session.add(sub)
        db.session.commit()
        flash('Subscription was added')
        return redirect(url_for('index'))
    return render_template('subscriptionform.html', title='Subscription', form=form)


def get_media_id(title, media_type):
    title = title.strip()
    query = sa.select(Media).where(f.lower(Media.title) == title.lower())
    existing_media = db.session.scalar(query)
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
        media_id = get_media_id(form.media_title.data, form.media_type.data)
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
