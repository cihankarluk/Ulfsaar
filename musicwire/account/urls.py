from django.urls import path

from musicwire.account import views

urlpatterns = [
    path('signup', views.UserSignUp.as_view(), name='singup'),
    path('signin', views.UserSignIn.as_view(), name='signin')
]