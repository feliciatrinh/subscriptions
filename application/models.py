import enum
from datetime import date
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from application import db


class FormEnum(enum.Enum):
    @classmethod
    def choices(cls):
        return [(choice, choice.name) for choice in cls]

    @classmethod
    def coerce(cls, item):
        return cls(str(item)) if not isinstance(item, cls) else item

    def __str__(self):
        return str(self.value)


class MediaType(FormEnum):
    tv = "tv"
    film = "film"

class PaymentFrequency(FormEnum):
    monthly = "monthly"
    yearly = "yearly"


class Media(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    title: so.Mapped[str] = so.mapped_column(sa.String, index=True, unique=True)
    type: so.Mapped[MediaType] = so.mapped_column(sa.Enum(
        MediaType,
        name="mediatype",
        create_constraint=True,
        validate_strings=True
    ))
    description: so.Mapped[Optional[str]] = so.mapped_column(sa.String)

    logs: so.WriteOnlyMapped['Log'] = so.relationship(back_populates='media')

    def __str__(self):
        return f'{self.title} is a {self.type} about {self.description}'

    def __repr__(self):
        return f'<Media(title={self.title}, type={self.type})>'


# TODO: add a function that returns id given name
class Subscription(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String, index=True, unique=True)
    # TODO: include a list of other names that should map to the same subscription e.g. Disney Plus is the same as Disney+
    cost: so.Mapped[str] = so.mapped_column(sa.String)
    payment_frequency: so.Mapped[PaymentFrequency] = so.mapped_column(
        sa.Enum(
            PaymentFrequency,
            name="paymentfrequency",
            create_constraint=True,
            validate_strings=True
        ),
        default=PaymentFrequency.monthly
    )
    active_date: so.Mapped[date] = so.mapped_column(sa.Date, index=True, default=lambda: date.today())
    inactive_date: so.Mapped[Optional[date]] = so.mapped_column(sa.Date)

    def __repr__(self):
        return f'<Subscription(id={self.id}, name={self.name}, cost={self.cost}, payment_frequency={self.payment_frequency})>'


class Log(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    date: so.Mapped[date] = so.mapped_column(sa.Date, index=True, default=lambda: date.today())
    subscription_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Subscription.id), index=True)
    media_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Media.id), index=True)
    season: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer)
    episode: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer)
    notes: so.Mapped[Optional[str]] = so.mapped_column(sa.String)

    media: so.Mapped[Media] = so.relationship(back_populates='logs')

    def __repr__(self):
        return f'<Log(id={self.id}, date={self.date}, subscription_id={self.subscription_id}, media_id={self.media_id})>'
