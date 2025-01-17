import enum
from datetime import date
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from sqlalchemy import func as f, cast, Float
from sqlalchemy.ext.hybrid import hybrid_property

from application import db


MONTHS_IN_YEAR = 12

class FormEnum(enum.Enum):
    @classmethod
    def choices(cls):
        return [(choice, str(choice)) for choice in cls]

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
    no_change = "no change"

    @classmethod
    def choices_on_create(cls):
        return [(choice, str(choice)) for choice in cls if choice != PaymentFrequency.no_change]


class Media(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    title: so.Mapped[str] = so.mapped_column(sa.String, index=True)
    type: so.Mapped[MediaType] = so.mapped_column(sa.Enum(
        MediaType,
        name="mediatype",
        create_constraint=True,
        validate_strings=True
    ))
    description: so.Mapped[Optional[str]] = so.mapped_column(sa.String)

    __table_args__ = (
        db.UniqueConstraint('title', 'type', name='_media_title_type_uc'),
    )

    def __str__(self):
        return f'{self.title} is a {self.type} about {self.description}'

    def __repr__(self):
        return f'<Media(title={self.title}, type={self.type})>'

    @classmethod
    def get_by_title_type(cls, title, type):
            query = sa.select(Media).where(f.lower(Media.title) == title.lower(), Media.type == type)
            return db.session.scalar(query)


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

    @hybrid_property
    def cost_to_float(self):
        return cast(self.cost, Float)

    @hybrid_property
    def monthly_cost(self):
        if self.payment_frequency == PaymentFrequency.monthly:
            return self.cost_to_float
        return self.cost_to_float / MONTHS_IN_YEAR

    @monthly_cost.expression
    def monthly_cost(cls):
        return sa.case((cls.payment_frequency == PaymentFrequency.monthly, cls.cost_to_float),
                       else_=(cls.cost_to_float / MONTHS_IN_YEAR)).label('monthly_cost')

    @hybrid_property
    def yearly_cost(self):
        if self.payment_frequency == PaymentFrequency.monthly:
            return self.cost_to_float * MONTHS_IN_YEAR
        return self.cost_to_float

    @yearly_cost.expression
    def yearly_cost(cls):
        return sa.case((cls.payment_frequency == PaymentFrequency.monthly, cls.cost_to_float * MONTHS_IN_YEAR),
                       else_=cls.cost_to_float).label('yearly_cost')

    @classmethod
    def get_by_name(cls, name):
        query = sa.select(Subscription).filter(f.lower(Subscription.name) == name.lower())
        return db.session.scalar(query)

    @classmethod
    def get(cls, filterby=None, orderby=None):
        query = sa.select(Subscription)
        if filterby is not None:
            query = query.filter(filterby)
        if orderby is not None:
            query = query.order_by(orderby)
        return db.session.scalars(query).all()

    @classmethod
    def total_monthly_cost(cls, exclude_inactive=True):
        query = db.session.query(f.sum(Subscription.monthly_cost))
        if exclude_inactive:
            query = query.filter(Subscription.inactive_date.is_(None))
        return query.scalar()

    @classmethod
    def total_yearly_cost(cls, exclude_inactive=True):
        query = db.session.query(f.sum(Subscription.yearly_cost))
        if exclude_inactive:
            query = query.filter(Subscription.inactive_date.is_(None))
        return query.scalar()


class Log(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    date: so.Mapped[date] = so.mapped_column(sa.Date, index=True, default=lambda: date.today())
    subscription_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Subscription.id), index=True)
    media_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Media.id), index=True)
    season: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer)
    episode: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer)
    notes: so.Mapped[Optional[str]] = so.mapped_column(sa.String)

    def __repr__(self):
        return f'<Log(id={self.id}, date={self.date}, subscription_id={self.subscription_id}, media_id={self.media_id})>'

    @classmethod
    def get_by_sub_id(cls, sub_id):
        query = sa.select(Log).filter(Log.subscription_id == sub_id)
        return db.session.scalars(query).all()

    @classmethod
    def get_by_media_id(cls, media_id):
        query = sa.select(Log).filter(Log.media_id == media_id)
        return db.session.scalars(query).all()

    @classmethod
    def get_by_sub_and_media(cls, sub_id, media_id):
        query = sa.select(Log).filter(Log.subscription_id == sub_id, Log.media_id == media_id)
        return db.session.scalars(query).all()

    @classmethod
    def most_logged_subs(cls):
        query = sa.select(Subscription.name, sa.func.count().label("count"))\
            .join(Log, Log.subscription_id == Subscription.id)\
            .group_by(Subscription.name)\
            .order_by(sa.desc("count"))
        return db.session.execute(query).all()

    @classmethod
    def most_logged_media(cls):
        query = sa.select(Media.title, sa.func.count().label("count"))\
            .join(Log, Log.media_id == Media.id)\
            .group_by(Media.title)\
            .order_by(sa.desc("count"))
        return db.session.execute(query).all()

    @classmethod
    def currently_watching(cls, limit=10):
        query = sa.select(Media.title).distinct()\
            .join(Log, Log.media_id == Media.id)\
            .order_by(Log.date.desc())\
            .limit(limit)
        return db.session.scalars(query).all()
