import datetime as datetime

from flask.ext.wtf import Form
from wtforms.fields import StringField, SubmitField, IntegerField, \
    TextAreaField, HiddenField, DateField, FileField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import (
    InputRequired,
    Regexp,
    Length,
    Optional,
    NumberRange,
    URL
)

from ..models import Agency
from .. import db


class IncidentReportForm(Form):
    vehicle_id = StringField('Vehicle ID', validators=[
        InputRequired('Vehicle ID is required.'),
        Length(min=2, max=10,
               message='Vehicle ID must be between 2 to 10 characters.'),
        Regexp("^[a-zA-Z0-9]*$",
               message='License plate number must '
                       'consist of only letters and numbers.'),
    ])

    license_plate = StringField('License Plate Number', validators=[
        Optional(),
        Regexp("^[a-zA-Z0-9]*$",
               message='License plate number must '
                       'consist of only letters and numbers.'),
        Length(min=6, max=7)
    ])

    bus_number = IntegerField('Bus Number', validators=[
        Optional()
    ])

    led_screen_number = IntegerField('LED Screen Number', validators=[
        Optional()
    ])

    latitude = HiddenField('Latitude')
    longitude = HiddenField('Longitude')
    location = StringField('Address')

    date = DateField('Date', default=datetime.date.today(),
                     validators=[InputRequired()])

    # TODO - add support for h:m:s format
    duration = IntegerField('Idling Duration (h:m:s)', validators=[
        InputRequired('Idling duration (hours:minutes:seconds) is required.'),
        NumberRange(min=0,
                    max=10000,
                    message='Idling duration must be between '
                            '0 and 10000 minutes.')
    ])

    agency = QuerySelectField('Vehicle Agency ',
                              validators=[InputRequired()],
                              get_label='name',
                              query_factory=lambda: db.session.query(Agency))

    picture = FileField('Upload a picture of the idling vehicle.',
                        validators=[Optional()])

    description = TextAreaField('Additional Notes', validators=[
        Optional(),
        Length(max=5000)
    ])

    submit = SubmitField('Create Report')


class EditIncidentReportForm(IncidentReportForm):
    # use picture URL instead of picture
    picture = StringField('Picture URL', validators=[
        URL(message='Picture URL must be a valid URL. '
                    'Please upload the image to an image hosting website '
                    'and paste the link into this field.')
    ])

    submit = SubmitField('Update Report')