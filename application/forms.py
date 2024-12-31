from flask_wtf import FlaskForm
from wtforms import DateField, DecimalField, SelectField, StringField, SubmitField
from wtforms.validators import ValidationError, DataRequired, InputRequired
import sqlalchemy as sa
from sqlalchemy import func as f
from application import db
from application.models import PaymentFrequency, Subscription

NAME_MAX_LENGTH = 64


class SubscriptionForm(FlaskForm):
    name = StringField(label='Subscription Service Name', validators=[DataRequired()])
    cost = DecimalField(label='Cost', validators=[InputRequired()])
    payment_frequency = SelectField(
        label='Payment Frequency',
        choices=PaymentFrequency.choices(),
        coerce=PaymentFrequency.coerce,
        default=PaymentFrequency.monthly
    )
    active_date = DateField('Active Date')
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
