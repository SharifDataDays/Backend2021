from decouple import config

from apps.accounts.models import User
from django.core.exceptions import ObjectDoesNotExist
import requests
import datetime

REGISTER_API = config('REGISTER_API')

def send_all_users(api):
    users = User.objects.all()
    serialized_info = []
    
    for user in users:
        try:
            serialized_info.append({
                'username': user.username,
                'email': user.email,
                'password': user.password,
                'full_name': '{} {}'.format(user.profile.firstname_fa, user.profile.lastname_fa),
                'full_name_english': '{} {}'.format(user.profile.firstname_en, user.profile.lastname_en),
                'university': user.profile.uni.name,
                'phone_number': user.profile.phone_number,
                'date_of_birth': '{}T{}Z'.format(datetime.date(2019, 8, 24), datetime.time(0, 0, 0)),
            })
        except ObjectDoesNotExist:
            User.objects.filter(username=user.username).update(is_active=False)

    for data in serialized_info:
        r = requests.post(api, data=data)
        if r.status_code != 201:
            User.objects.filter(username=data.get('username')).update(is_active=False)
