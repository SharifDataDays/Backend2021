import secrets
import requests
import datetime

from django.core.exceptions import ObjectDoesNotExist

from rest_framework import status, permissions
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from apps.accounts.serializers import *
from apps.accounts.models import ResetPasswordToken, ActivateUserToken, University
from apps.accounts.utils import REGISTER_API

class SignUpView(GenericAPIView):
    queryset = Profile.objects.all()
    serializer_class = UserSignUpSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):

            # activate_user_token = ActivateUserToken(
            #         token=secrets.token_urlsafe(32),
            #         eid=urlsafe_base64_encode(force_bytes(serializer.validated_data['email'])),
            #         )
            # activate_user_token.save()
            # context = {
            #     'domain': 'datadays.ir',
            #     'eid': activate_user_token.eid,
            #     'token': activate_user_token.token,
            # }
            # email_html_message = render_to_string('accounts/email/user_activate_email.html', context)
            # email_plaintext_message = render_to_string('accounts/email/user_activate_email.txt', context)
            # msg = EmailMultiAlternatives(
            #         _("Activate Account for {title}".format(title="DataDays")),
            #         email_plaintext_message,
            #         "datadays.sharif.ssc@gmail.com",
            #         [serializer.validated_data['email']]
            #     )
            # msg.attach_alternative(email_html_message, "text/html")
            try:
                # msg.send()
                serializer.save()
                serializer.instance.is_active = True
                serializer.instance.save()
            except Exception as e:
                return Response({'detail': 'Invalid email or user has not been saved.'}, status=406)

            user = User.objects.get(username=serializer.get('username'))
            try:
                data = {
                    'username': user.username,
                    'email': user.email,
                    'password': user.password,
                    'full_name': '{} {}'.format(user.profile.firstname_fa, user.profile.lastname_fa),
                    'full_name_english': '{} {}'.format(user.profile.firstname_en, user.profile.lastname_en),
                    'university': user.profile.uni.name,
                    'phone_number': user.profile.phone_number,
                    'date_of_birth': '{}T{}Z'.format(user.profile.birth_date, datetime.time(0, 0, 0)),}
                    
                r = requests.post(REGISTER_API, data=data)
                if r.status_code != 201:
                    user.update(is_active=False)

            except ObjectDoesNotExist:
                user.update(is_active=False)

            return Response({'detail': 'User created successfully. Check your email for confirmation link'}, status=200)
        else:
            return Response({'error': 'Error occurred during User creation'}, status=500)


class ActivateView(GenericAPIView):

    def get(self, request, eid, token):
        activate_user_token = get_object_or_404(ActivateUserToken,
                eid=eid, token=token)

        email = urlsafe_base64_decode(activate_user_token.eid).decode('utf-8')
        user = get_object_or_404(User, email=email)
        user.is_active = True
        user.save()

        # TODO: redirect to a valid address
        return redirect('http://datadays.ir/login')


class LogoutView(GenericAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)


class ResetPasswordView(GenericAPIView):
    serializer_class = ResetPasswordSerializer

    def post(self, request):
        data = self.get_serializer(request.data).data

        user = get_object_or_404(User, email=data['email'].lower())

        uid = urlsafe_base64_encode(force_bytes(user.id))
        ResetPasswordToken.objects.filter(uid=uid).delete()
        reset_password_token = ResetPasswordToken(
                uid=uid,
                token=secrets.token_urlsafe(32),
                expiration_date=timezone.now() + timezone.timedelta(hours=24),
            )
        reset_password_token.save()

        context = {
            'domain': 'datadays.sharif.edu',
            'username': user.username,
            'uid': reset_password_token.uid,
            'token': reset_password_token.token,
        }
        email_html_message = render_to_string('accounts/email/user_reset_password.html', context)
        email_plaintext_message = render_to_string('accounts/email/user_reset_password.txt', context)
        msg = EmailMultiAlternatives(
                _("Password Reset for {title}".format(title="DataDays")),
                email_plaintext_message,
                "datadays.sharif@gmail.com",
                [user.email]
            )
        msg.attach_alternative(email_html_message, "text/html")
        msg.send()

        return Response({'detail': 'Successfully Sent Reset Password Email'}, status=200)


class ResetPasswordConfirmView(GenericAPIView):
    serializer_class = ResetPasswordConfirmSerializer

    def post(self, request):
        data = self.get_serializer(request.data).data

        rs_token = get_object_or_404(ResetPasswordToken, uid=data['uid'], token=data['token'])
        if (timezone.now() - rs_token.expiration_date).total_seconds() > 24 * 60 * 60:
            return Response({'error': 'Token Expired'}, status=400)

        user = get_object_or_404(User, id=urlsafe_base64_decode(data['uid']).decode('utf-8'))
        user.password = make_password(data['new_password1'])
        user.save()
        return Response({'detail': 'Successfully Changed Password'}, status=200)


class ProfileView(GenericAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        data = self.get_serializer(user).data
        return Response(data=data, status=HTTP_200_OK)

    def put(self, request):
        user = request.user
        serializer = self.get_serializer(instance=user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(serializer.data)


class ChangePasswordAPIView(GenericAPIView):
    queryset = User.objects.all()
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.data

        if not request.user.check_password(data['old_password']):
            return Response({'detail': 'incorrect current password'}, status=406)

        request.user.password = make_password(data['new_password1'])
        request.user.save()
        return Response({'detail': 'password changed successfully'}, status=200)


class UniversityAPIView(GenericAPIView):
    serializer_class = UniversitySerializer
    queryset = University.objects.all()

    def get(self, request):
        return Response(self.get_serializer(self.get_queryset(), many=True, read_only=True).data)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)

