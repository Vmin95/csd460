from django.urls import path
from . import views

urlpatterns = [
    path("api/register", views.register_api, name="api_register"),
    path("api/login",    views.login_api,    name="api_login"),
    path("api/logout",   views.logout_api,   name="api_logout"),
    path("api/me",       views.me_api,       name="api_me"),
]