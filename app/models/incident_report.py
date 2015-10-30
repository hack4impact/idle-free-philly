from .. import db
from . import Agency


class Location(db.Model):
    __tablename__ = 'locations'
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.String(50))
    longitude = db.Column(db.String(50))
    original_user_text = db.Column(db.Text)  # the raw text which we geocoded
    incident_report_id = db.Column(db.Integer,
                                   db.ForeignKey('incident_reports.id'))


class IncidentReport(db.Model):
    __tablename__ = 'incident_reports'
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.String(8))
    license_plate = db.Column(db.String(8))
    location = db.relationship('Location',
                               uselist=False,
                               lazy='joined',
                               backref='incident_report')
    date = db.Column(db.DateTime)  # hour the incident occurred
    duration = db.Column(db.Interval)  # like timedelta object
    agency_id = db.Column(db.Integer, db.ForeignKey('agencies.id'))
    picture_url = db.Column(db.Text)
    description = db.Column(db.Text)

    @staticmethod
    def generate_fake(count=100, **kwargs):
        """Generate a number of fake reports for testing."""
        from sqlalchemy.exc import IntegrityError
        from random import seed, choice, randint
        from datetime import timedelta
        from faker import Faker

        def flip_coin():
            """Returns True or False with equal probability"""
            return choice([True, False])

        agencies = Agency.query.all()
        fake = Faker()

        seed()
        for i in range(count):
            l = Location(
                original_user_text=fake.address(),
                latitude=str(fake.geo_coordinate(center=39.951021,
                                                 radius=0.001)),
                longitude=str(fake.geo_coordinate(center=-75.197243,
                                                  radius=0.001))
            )
            r = IncidentReport(
                vehicle_id=fake.password(length=6, lower_case=False),
                # Either sets license plate to '' or random 6 character string
                license_plate=fake.password(length=6, lower_case=False)
                if flip_coin() else '',
                location=l,
                date=fake.date_time_between(start_date="-1y", end_date="now"),
                duration=timedelta(minutes=randint(1, 30)),
                agency=choice(agencies),
                picture_url=fake.image_url(),
                description=fake.paragraph(),
                **kwargs
            )
            db.session.add(r)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()