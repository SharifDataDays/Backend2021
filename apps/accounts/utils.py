from apps.accounts.models import User
from django.core.exceptions import ObjectDoesNotExist
import requests
import datetime

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
                'city': 'tehran',
                'phone_number': user.profile.phone_number,
                'gender': 1,
                'date_of_birth': '{}T{}Z'.format(datetime.date(2019, 8, 24), datetime.time(0, 0, 0)),
            })
        except ObjectDoesNotExist:
            User.objects.get(username=user.username).update(is_active=False)
            print(user.username)

    for data in serialized_info:
        r = requests.post(api, data=data)
        if r.status_code != 201:
            User.objects.get(username=data.get('username')).update(is_active=False)
