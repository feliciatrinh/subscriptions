import os
os.environ['DATABASE_URL'] = 'sqlite://'

import unittest
import sqlalchemy as sa
from datetime import date, timedelta
from application import app, db
from application.models import Log, Media, MediaType, PaymentFrequency, Subscription

NETFLIX = "Netflix"
PEACOCK = "Peacock"
INSIDE_OUT = "Inside Out"
INSIDE_OUT_2 = "Inside Out 2"

current_date = date.today()
yesterday = current_date - timedelta(days=1)
tomorrow = current_date + timedelta(days=1)


class ModelCase(unittest.TestCase):
    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()


class SubscriptionModelCase(ModelCase):
    def test_subscription(self):
        sub1 = Subscription(name=NETFLIX, cost="22.99")
        db.session.add(sub1)
        result = db.session.scalar(sa.select(Subscription).where(Subscription.name == NETFLIX))
        self.assertEqual(result.payment_frequency, PaymentFrequency.monthly)
        self.assertEqual(result.active_date, current_date)
        self.assertIsNone(result.inactive_date)

        sub2 = Subscription(name=PEACOCK, cost="0.00", payment_frequency=PaymentFrequency.yearly, active_date=yesterday, inactive_date=tomorrow)
        db.session.add(sub2)
        result = db.session.scalar(sa.select(Subscription).where(Subscription.name == PEACOCK))
        self.assertEqual(result.payment_frequency, PaymentFrequency.yearly)
        self.assertEqual(result.active_date, yesterday)
        self.assertEqual(result.inactive_date, tomorrow)

        self.assertEqual(len(Subscription.query.all()), 2)

        # Subscription names should be unique
        duplicate = Subscription(name=NETFLIX, cost="0.00")
        with self.assertRaises(sa.exc.IntegrityError):
            db.session.add(duplicate)
            db.session.flush()

    def test_subscription_payment(self):
        # Subscription payment frequency is invalid
        bad_payment = Subscription(name="bad payment", cost="0.00", payment_frequency="dne")
        with self.assertRaises(sa.exc.StatementError):
            db.session.add(bad_payment)
            db.session.flush()

    def test_get_by_name(self):
        sub = Subscription(name=NETFLIX, cost="22.99")
        db.session.add(sub)
        result = Subscription.get_by_name(NETFLIX.upper())
        self.assertEqual(result.name, NETFLIX)


class MediaModelCase(ModelCase):
    def test_media(self):
        media = Media(title=INSIDE_OUT, type=MediaType.film)
        db.session.add(media)
        result = db.session.scalar(sa.select(Media).where(Media.title == INSIDE_OUT))
        self.assertEqual(result.type, MediaType.film)
        self.assertIsNone(result.description)

    def test_media_type(self):
        # media type is invalid
        bad_media_type = Media(title="bad media", type="dne")
        with self.assertRaises(sa.exc.StatementError):
            db.session.add(bad_media_type)
            db.session.flush()

    def test_get_by_title_type(self):
        media = Media(title=INSIDE_OUT_2, type=MediaType.film)
        db.session.add(media)
        result = Media.get_by_title_type(INSIDE_OUT_2.upper(), MediaType.film)
        self.assertEqual(result.title, INSIDE_OUT_2)
        self.assertEqual(result.type, MediaType.film)

        result2 = Media.get_by_title_type(INSIDE_OUT_2.upper(), MediaType.tv)
        self.assertIsNone(result2)

    def test_media_unique_constraint(self):
        media1 = Media(title=INSIDE_OUT, type=MediaType.film)
        media2 = Media(title=INSIDE_OUT, type=MediaType.tv)
        db.session.add_all((media1, media2))
        self.assertEqual(len(Media.query.all()), 2)

        duplicate = Media(title=INSIDE_OUT, type=MediaType.film, description="emotions")
        with self.assertRaises(sa.exc.IntegrityError):
            db.session.add(duplicate)
            db.session.flush()


class LogModelCase(ModelCase):
    def test_log(self):
        sub = Subscription(name=PEACOCK, cost="0.00")
        media = Media(title=INSIDE_OUT, type=MediaType.film)
        db.session.add_all((sub, media))

        sub_id = Subscription.get_by_name(PEACOCK).id
        media_id = Media.get_by_title_type(INSIDE_OUT, MediaType.film).id

        log = Log(subscription_id=sub_id, media_id=media_id)
        db.session.add(log)

        result = db.session.scalar(sa.select(Log).where(Log.subscription_id == sub_id, Log.media_id == media_id))
        self.assertEqual(result.date, current_date)
        self.assertIsNone(result.season)
        self.assertIsNone(result.episode)
        self.assertIsNone(result.notes)
        self.assertEqual(result.media.id, media_id)
        self.assertEqual(result.subscription.id, sub_id)

        media2 = Media(title=INSIDE_OUT_2, type=MediaType.film)
        db.session.add(media2)
        media2_id = Media.get_by_title_type(INSIDE_OUT_2, MediaType.film).id

        log2 = Log(subscription_id=sub_id, media_id=media2_id, date=tomorrow, season=1, episode=1, notes="Amazing!")
        db.session.add(log2)

        result2 = db.session.scalar(sa.select(Log).where(Log.subscription_id == sub_id, Log.media_id == media2_id))
        self.assertEqual(result2.date, tomorrow)
        self.assertEqual(result2.season, 1)
        self.assertEqual(result2.episode, 1)
        self.assertEqual(result2.notes, "Amazing!")
        self.assertEqual(result2.media.id, media2_id)
        self.assertEqual(result2.subscription.id, sub_id)

        self.assertEqual(len(Log.query.all()), 2)

    def test_log_missing_sub(self):
        # subscription_id does not exist
        media = Media(title=INSIDE_OUT, type=MediaType.film)
        db.session.add(media)
        media_id = Media.get_by_title_type(INSIDE_OUT, MediaType.film).id
        log = Log(subscription_id=999, media_id=media_id)
        with self.assertRaises(sa.exc.IntegrityError):
            db.session.add(log)
            db.session.flush()

    def test_log_missing_media(self):
        # media_id does not exist
        sub = Subscription(name=PEACOCK, cost="0.00")
        db.session.add(sub)
        sub_id = Subscription.get_by_name(PEACOCK).id
        log = Log(subscription_id=sub_id, media_id=999)
        with self.assertRaises(sa.exc.IntegrityError):
            db.session.add(log)
            db.session.flush()

    def test_get_by_sub_id(self):
        sub1 = Subscription(name=PEACOCK, cost="0.00")
        sub2 = Subscription(name=NETFLIX, cost="0.00")
        media = Media(title=INSIDE_OUT, type=MediaType.film)
        db.session.add_all((sub1, sub2, media))

        sub_id = Subscription.get_by_name(PEACOCK).id
        sub_id_ignored = Subscription.get_by_name(NETFLIX).id
        media_id = Media.get_by_title_type(INSIDE_OUT, MediaType.film).id
        log1 = Log(subscription_id=sub_id, media_id=media_id, date=yesterday)
        log2 = Log(subscription_id=sub_id, media_id=media_id)
        log3 = Log(subscription_id=sub_id_ignored, media_id=media_id)
        db.session.add_all((log1, log2, log3))
        result = Log.get_by_sub_id(sub_id)
        self.assertEqual(len(result), 2)
        self.assertSetEqual({res.subscription_id for res in result}, {sub_id})

        no_results = Log.get_by_sub_id(999)
        self.assertListEqual(no_results, [])

    def test_get_by_media_id(self):
        sub = Subscription(name=PEACOCK, cost="0.00")
        media1 = Media(title=INSIDE_OUT, type=MediaType.film)
        media2 = Media(title=INSIDE_OUT_2, type=MediaType.film)
        db.session.add_all((sub, media1, media2))

        sub_id = Subscription.get_by_name(PEACOCK).id
        media_id = Media.get_by_title_type(INSIDE_OUT, MediaType.film).id
        media_id_ignored = Media.get_by_title_type(INSIDE_OUT_2, MediaType.film).id
        log1 = Log(subscription_id=sub_id, media_id=media_id, date=yesterday)
        log2 = Log(subscription_id=sub_id, media_id=media_id)
        log3 = Log(subscription_id=sub_id, media_id=media_id_ignored)
        db.session.add_all((log1, log2, log3))
        result = Log.get_by_media_id(media_id)
        self.assertEqual(len(result), 2)
        self.assertSetEqual({res.media_id for res in result}, {media_id})

        no_results = Log.get_by_media_id(999)
        self.assertListEqual(no_results, [])

    def test_get_by_sub_media(self):
        sub = Subscription(name=PEACOCK, cost="0.00")
        media1 = Media(title=INSIDE_OUT, type=MediaType.film)
        media2 = Media(title=INSIDE_OUT_2, type=MediaType.film)
        db.session.add_all((sub, media1, media2))

        sub_id = Subscription.get_by_name(PEACOCK).id
        media_id = Media.get_by_title_type(INSIDE_OUT, MediaType.film).id
        media_id_ignored = Media.get_by_title_type(INSIDE_OUT_2, MediaType.film).id
        log1 = Log(subscription_id=sub_id, media_id=media_id)
        log2 = Log(subscription_id=sub_id, media_id=media_id_ignored)
        db.session.add_all((log1, log2))
        result = Log.get_by_sub_and_media(sub_id, media_id)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].subscription_id, sub_id)
        self.assertEqual(result[0].media_id, media_id)

if __name__ == '__main__':
    unittest.main(verbosity=2)
