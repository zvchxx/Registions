from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from conf.settings import EMAIL_HOST_USER
from account.form import RegistrationForm, LoginForm
from account.token import email_verification_token


def verify_email(request, uidb64, token):
    uid = force_str(urlsafe_base64_decode(uidb64))
    user = User.objects.get(pk=uid)
    if user is not None and email_verification_token.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect(reverse_lazy('users:login'))
    else:
        return render(request, '/')


def send_email_verification(request, user):
    token = email_verification_token.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    current_site = get_current_site(request)
    verification_url = reverse('users:verify-email', kwargs={'uidb64': uid, 'token': token})
    full_url = f"http://{current_site.domain}{verification_url}"

    text_content = render_to_string(
        'registions/verify_email.html',
        {'user': user, 'full_url': full_url}
    )

    message = EmailMultiAlternatives(
        subject="Verification Email",
        body=text_content,
        to=[user.email],
        from_email=EMAIL_HOST_USER
    )
    message.attach_alternative(text_content, 'text/html')
    message.send()


def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])  
            user.is_active = False
            user.save()
            send_email_verification(request, user)
            return redirect(reverse_lazy('users:login'))
        else:
            errors = form.errors.as_json()      
            return render(request, '/', {"errors": errors})
    else:
        return render(request, 'registions/register.html')


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request=request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                return render(request, 'registions/login.html')
        else:
            return render(request, 'registions/login.html')
    else:
        return render(request, 'registions/login.html')


def logout_view(request):
    logout(request)
    return redirect('/')