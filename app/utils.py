import re
import requests
from redis import Redis
from flask import url_for, current_app
from imgurpython import ImgurClient
from rq_scheduler import Scheduler


def register_template_utils(app):
    """Register Jinja 2 helpers (called from __init__.py)."""

    @app.template_test()
    def equalto(value, other):
        return value == other

    @app.template_global()
    def is_hidden_field(field):
        from wtforms.fields import HiddenField
        return isinstance(field, HiddenField)

    app.add_template_global(index_for_role)


def index_for_role(role):
    return url_for(role.index)


def parse_phone_number(phone_number):
    """Make phone number conform to E.164 (https://en.wikipedia.org/wiki/E.164)
    """
    stripped = re.sub(r'\D', '', phone_number)
    if len(stripped) == 10:
        stripped = '1' + stripped
    stripped = '+' + stripped
    return stripped


def strip_non_alphanumeric_chars(input_string):
    """Strip all non-alphanumeric characters from the input."""
    stripped = re.sub('[\W_]+', '', input_string)
    return stripped


# Viewport-biased geocoding using Google API
# Returns a tuple of (latitude, longitude), (None, None) if geocoding fails
def geocode(address):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    payload = {'address': address, 'bounds': current_app.config['VIEWPORT']}
    r = requests.get(url, params=payload)
    if r.json()['status'] is 'ZERO_RESULTS' or len(r.json()['results']) is 0:
        return None, None
    else:
        coords = r.json()['results'][0]['geometry']['location']
        return coords['lat'], coords['lng']


def upload_image(imgur_client_id, imgur_client_secret, app_name,
                 image_url=None, image_file_path=None):
    """Uploads an image to Imgur by the image's url or file_path. Returns the
    Imgur api response."""
    if image_url is None and image_file_path is None:
        raise ValueError('Either image_url or image_file_path must be '
                         'supplied.')
    client = ImgurClient(imgur_client_id, imgur_client_secret)
    title = '{} Image Upload'.format(current_app.config['APP_NAME'])

    description = 'This is part of an idling vehicle report on {}.'.format(
        current_app.config['APP_NAME'])

    if image_url is not None:
        result = client.upload_from_url(url=image_url, config={
            'title': title,
            'description': description,
        })
    else:
        result = client.upload_from_path(path=image_file_path, config={
            'title': title,
            'description': description,
        })

    return result['link'], result['deletehash']


def get_rq_scheduler(app=current_app):
    conn = Redis(
        host=app.config['RQ_DEFAULT_HOST'],
        port=app.config['RQ_DEFAULT_PORT'],
        db=0,
        password=app.config['RQ_DEFAULT_PASSWORD']
    )
    return Scheduler(connection=conn)  # Get a scheduler for the default queue
