from flask_wtf import FlaskForm
from wtforms import DateField, DecimalField, IntegerField, SelectField, StringField, SubmitField, validators
from wtforms.validators import ValidationError, DataRequired, InputRequired
import sqlalchemy as sa
from sqlalchemy import func as f
from application import db
from application.models import MediaType, PaymentFrequency, Subscription

NAME_MAX_LENGTH = 64
NOTES_MAX_LENGTH = 256
MEDIA_NAME_MAX_LENGTH = 256


class SubscriptionForm(FlaskForm):
    name = StringField(label='Subscription Service Name', validators=[DataRequired()])
    cost = DecimalField(label='Cost', validators=[InputRequired()])
    payment_frequency = SelectField(
        label='Payment Frequency',
        choices=PaymentFrequency.choices_on_create(),
        coerce=PaymentFrequency.coerce,
        default=PaymentFrequency.monthly
    )
    active_date = DateField('Active Date', validators=[validators.optional()])
    submit = SubmitField('Submit')

    def validate_name(self, name):
        name.data = name.data.strip()
        if len(name.data) > NAME_MAX_LENGTH:
            raise ValidationError(f'Name exceeds maximum length of {NAME_MAX_LENGTH}')
        existing_subscription = db.session.scalar(sa.select(Subscription).where(
            f.lower(Subscription.name) == name.data.lower()
        ))
        if existing_subscription:
            raise ValidationError('Subscription already exists')

class EditSubscriptionForm(FlaskForm):
    subscription = SelectField(label='Subscription Service Name', validators=[DataRequired()])
    cost = DecimalField(label='Cost', validators=[validators.optional()])
    payment_frequency = SelectField(
        label='Payment Frequency',
        choices=PaymentFrequency.choices(),
        coerce=PaymentFrequency.coerce,
        default=PaymentFrequency.no_change
    )
    active_date = DateField('Active Date', validators=[validators.optional()])
    inactive_date = DateField('Inactive Date', validators=[validators.optional()])
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subscription.choices = [(c.id, c.name) for c in Subscription.query.all()]

    def put(self, url, **kwargs):
        return self.form.send(url, method='PUT', **kwargs)


class LogForm(FlaskForm):
    subscription = SelectField(label='Subscription Service Name', validators=[DataRequired()])
    date = DateField('Date Watched', validators=[validators.optional()])
    media_title = StringField(
        label='Media Name (e.g. Film title, TV show name)',
        validators=[DataRequired(), validators.length(max=MEDIA_NAME_MAX_LENGTH)]
    )
    media_type = SelectField(
        label='Media Type',
        choices=MediaType.choices(),
        coerce=MediaType.coerce,
        default=MediaType.film
    )
    season_number = IntegerField(label='Season Number', validators=[validators.optional()])
    episode_number = IntegerField(label='Episode Number', validators=[validators.optional()])
    notes = StringField(label='Notes', validators=[validators.optional(), validators.length(max=NOTES_MAX_LENGTH)])

    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subscription.choices = [(c.id, c.name) for c in Subscription.query.all()]
