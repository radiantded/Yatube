from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('logout/', LogoutView.as_view(template_name='logged_out.html'),
      name='logout')
]
