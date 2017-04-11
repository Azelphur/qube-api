import requests
import time
from datetime import datetime
from collections import namedtuple
from qube.errors import *

House = namedtuple('House', [
    'uuid',
    'updated_at', 
    'rooms'
])

Room = namedtuple('Room', [
    'uuid',
    'updated_at',
    'appliances'
])

Appliance = namedtuple('Appliance', [
    'uuid',
    'led_state',
    'rgbw1',
    'rgbw2',
    'rgbw3',
    'status_updated_at',
    'updated_at'
])

Mood = namedtuple('Mood', [
    'uuid',
    'type_id',
    'updated_at'
])

STATE_ON = 17
STATE_OFF = 0

class Qube(object):
    BASE_URL = 'https://home.qube-smarthome.com/api/v1'

    def __init__(self, email, password):
        self.session = requests.Session()
        self.access_token = None
        self.access_token_expires_at = None
        self.email = email
        self.password = password
        self.get_access_token()

    def get_access_token(self):
        data = {
            'email': self.email,
            'password': self.password,
            'grantType': 'password'
        }
        response = self._request('POST', '/auth/tokens', data=data)
        self.access_token = response['data']['accessToken']
        self.access_token_expires_at = time.time() + int(response['data']['expiresIn'])
        self.refresh_token = response['data']['refreshToken']

    def get_users(self):
        params = {
            'expand': 'houses,rooms,appliances,status,moods,pids',
            'userFields': 'houses,email,moods,pids',
            'houseFields': 'houseClientUUID,updatedAt,rooms',
            'roomFields': 'roomClientUUID,updatedAt,appliances',
            'applianceFields': 'applianceClientUUID,updatedAt,status', 
            'moodFields': 'moodClientUUID,moodTypeID,updatedAt',
            'pidFields': 'pidClientUUID,updatedAt'
        }
        response = self._request('GET', '/users', params=params)
        houses = []
        for house in response['data']['houses']:
            rooms = []
            for room in house['rooms']:
                appliances = []
                for appliance in room['appliances']:
                    appliances.append(
                        Appliance(
                            uuid=appliance['applianceClientUUID'],
                            led_state=appliance['ledState'],
                            rgbw1=appliance['rgbw1'],
                            rgbw2=appliance['rgbw2'],
                            rgbw3=appliance['rgbw3'],
                            status_updated_at=datetime.strptime(appliance['statusUpdatedAt'], "%Y-%m-%dT%H:%M:%S.%fZ"),
                            updated_at=datetime.strptime(appliance['updatedAt'], "%Y-%m-%dT%H:%M:%S.%fZ"),
                        )
                    )
                rooms.append(
                    Room(
                        uuid=room['roomClientUUID'],
                        updated_at=datetime.strptime(appliance['updatedAt'], "%Y-%m-%dT%H:%M:%S.%fZ"),
                        appliances=appliances
                    )
                )
            houses.append(
                House(
                    uuid='houseClientUUID',
                    updated_at=datetime.strptime(appliance['updatedAt'], "%Y-%m-%dT%H:%M:%S.%fZ"),
                    rooms=rooms
                )
            )
        moods = []
        for mood in response['data']['moods']:
            moods.append(
                Mood(
                    uuid=mood['moodClientUUID'],
                    type_id=mood['moodTypeID'],
                    updated_at=datetime.strptime(mood['updatedAt'], "%Y-%m-%dT%H:%M:%S.%fZ"),
                )
            )
        return houses, moods

    def set_appliance(self, appliance_id, color, brightness):
        data = {
            'rgbw1': color,
            'state': brightness
        }
        self._request('PUT', '/cmd_appliances/'+appliance_id+'/led', json=data)

    def _request(self, method, path, **kwargs):
        if self.access_token:
            if self.access_token_expires_at < time.time():
                self.get_access_token()
            headers = {
                'Authorization': 'Bearer {}'.format(self.access_token)
            }
        else:
            headers = {}
        try:
            r = self.session.request(method, self.BASE_URL + path, headers=headers, **kwargs)
            response = r.json()
            if response['status'] == 'fail':
                if response['data']['code'] == 3:
                    raise InvalidTokenError(response['data']['code'], response['data']['message'])
        except (requests.ConnectionError, requests.Timeout) as e:
            raise errors.Unavailable() from e
        return r.json()
