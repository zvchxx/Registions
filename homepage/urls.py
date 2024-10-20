from django.urls import path

from homepage import views


app_name = 'home'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
]