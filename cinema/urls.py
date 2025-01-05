from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from django.urls import path, reverse_lazy

from .forms import CustomSetPasswordForm, CustomPasswordResetForm
from .views import *


urlpatterns = [
    path('', index, name='index'),
    path('<str:model_name>/<slug:slug>/', detail, name='detail'),
    path('movies/', movies, name='movies'),
    path('tvshows/', tvshows, name='serials'),
    path('genre/', genre, name='genre'),
    path('cartoon/', cartoon, name='cartoon'),
    path('signup/', signup, name='signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password-reset/',
         auth_views.PasswordResetView.as_view(template_name='cinema/registration/password_reset_form.html',
                                              form_class=CustomPasswordResetForm,
                                              email_template_name='cinema/registration/password_reset_email.html',
                                              success_url=reverse_lazy("password_reset_done")),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='cinema/registration/password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='cinema/registration/password_reset_confirm.html',
                                                     form_class=CustomSetPasswordForm,

                                                     success_url=reverse_lazy(
                                                         "password_reset_complete")),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='cinema/registration/password_reset_complete.html'),
         name='password_reset_complete')

]
