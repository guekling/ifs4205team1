from django.contrib.auth import (
  login as auth_login
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect

from core.models import User
from mobileregister.forms import DeviceInforForm


class UserLogin(LoginView):
  """
  Custom user login view that extends from Django's LoginView
  """
  form_class = AuthenticationForm
  template_name = 'user_login.html'

  def form_valid(self, form):
    """
    Checks if a user is a valid user
    """
    try:
      user = form.get_user()
    except User.DoesNotExist:
      user = None

    if user is not None:
      if len(user.hashed_last_six) > 0 and len(user.hashed_id) > 0:
        return redirect("repeat_register", user_id=user.uid)
      else:
        auth_login(self.request, form.get_user())
        return redirect('user_register', user_id=user.uid)

    else:
      form = AuthenticationForm

      context = {
        'form': form,
      }

      return render(self.request, 'user_login.html', context)

@login_required(login_url='/mobileregister/login/')
def user_register(request, user_id):
  # the session will expire 1 minutes after inactivity, and will require log in again.
  request.session.set_expiry(60)

  user = user_does_not_exists(user_id)

  # when user purposefully try to traverse to this url but they already registered
  if len(user.hashed_last_six) > 0 and len(user.hashed_id) > 0:
    return redirect("repeat_register", user_id=user.uid)

  form = DeviceInforForm(request.POST or None)

  if form.is_valid():
    cd = form.cleaned_data
    infor = cd.get('infor')
    user.hashed_id = infor[:64]
    user.hashed_last_six = infor[64:]
    user.save()
    return redirect('success_register', user_id=user.uid)

  else:
    context = {
      'form': DeviceInforForm(),
    }
    return render(request, "user_register.html", context)

@login_required(login_url='/mobileregister/login/')
def repeat_register(request, user_id):
  user = user_does_not_exists(user_id)

  # when user purposefully try to traverse to this url but they haven't register
  if len(user.hashed_last_six) == 0 and len(user.hashed_id) == 0:
    return redirect("user_register", user_id=user.uid)

  return render(request, "repeat_register.html")

@login_required(login_url='/mobileregister/login/')
def success_register(request, user_id):
  user = user_does_not_exists(user_id)

  # when user purposefully try to traverse to this url but they haven't registered
  if len(user.hashed_last_six) == 0 and len(user.hashed_id) == 0:
    return redirect("user_register", user_id=user.uid)

  return render(request, "success_register.html")

##########################################
############ Helper Functions ############
##########################################

def user_does_not_exists(user_id):
  """
  Redirects to login if user_id is invalid
  """
  try:
    return User.objects.get(uid=user_id)
  except User.DoesNotExist:
    redirect('user_login')


