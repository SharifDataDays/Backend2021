from decouple import config

from apps.accounts.models import User
from django.core.exceptions import ObjectDoesNotExist
import requests
import datetime

REGISTER_API = config('REGISTER_API')

def send_all_users():
    users = User.objects.filter(is_active=False)
    serialized_info = []
    
    for user in users:
        try:
            serialized_info.append({
                'username': user.username,
                'email': user.email,
                'full_name': '{} {}'.format(user.profile.firstname_fa, user.profile.lastname_fa),
                'full_name_english': '{} {}'.format(user.profile.firstname_en, user.profile.lastname_en),
                'university': user.profile.uni.name,
                'phone_number': user.profile.phone_number,
                'date_of_birth': '{}T00:00:00Z'.format(user.profile.birth_date)
            })
        except ObjectDoesNotExist:
            continue

    for data in serialized_info:
        r = requests.post(REGISTER_API, data=data)
        if r.status_code == 201:
            User.objects.filter(username=data.get('username')).update(is_active=True)


def register_user(user):
    user.is_active = True
    try:
        data = {
            'username': user.username,
            'email': user.email,
            'password': user.password,
            'full_name': '{} {}'.format(user.profile.firstname_fa, user.profile.lastname_fa),
            'full_name_english': '{} {}'.format(user.profile.firstname_en, user.profile.lastname_en),
            'university': user.profile.uni.name,
            'phone_number': user.profile.phone_number,
            'date_of_birth': '{}T00:00:00Z'.format(user.profile.birth_date)}
            
        r = requests.post(REGISTER_API, data=data)
        if r.status_code != 201:
            user.is_active = False
    except ObjectDoesNotExist:
        user.is_active = True
    user.save()
