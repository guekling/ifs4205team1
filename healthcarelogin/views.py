from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from django.contrib.auth import (
    REDIRECT_FIELD_NAME, get_user_model, login as auth_login
)
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView

from patientlogin.forms import UserEditForm

from core.models import User, Healthcare

class HealthcareLogin(LoginView):
  """
  Custom healthcare professional login view that extends from Django's LoginView
  """
  form_class = AuthenticationForm
  template_name = 'healthcare_login.html'

  def form_valid(self, form):
    """
    Checks if a user is a healthcare professional
    """
    try:
      healthcare = form.get_user().healthcare
    except Healthcare.DoesNotExist:
      healthcare = None

    if healthcare is not None:
      auth_login(self.request, form.get_user())
      return redirect('healthcare_dashboard', healthcare_id=healthcare.id)
    else:
      form = AuthenticationForm

      context = {
        'form': form,
      }

      return render(self.request, 'healthcare_login.html', context)

class HealthcareLogout(LogoutView):
  """
  Custom healthcare logout view that extends from Django's LogoutView
  """
  next_page = '/healthcare/login'

class HealthcareChangePassword(PasswordChangeView):
  """
  Custom healthcare change password view that extends from Django's PasswordChangeView
  """
  form_class = PasswordChangeForm
  template_name = 'healthcare_change_password.html'

  def get_success_url(self):
    user = self.request.user
    url = reverse_lazy('healthcare_change_password_complete', kwargs={'healthcare_id': user.healthcare.id})
    return url

class HealthcareChangePasswordComplete(PasswordChangeDoneView):
  """
  Custom healthcare change password complete view that extends from Django's PasswordChangeDoneView
  """
  template_name = 'healthcare_change_password_complete.html'

@login_required(login_url='/healthcare/login/')
@user_passes_test(lambda u: u.is_healthcare, login_url='/healthcare/login/')
def healthcare_settings(request, healthcare_id):
  healthcare = healthcare_does_not_exists(healthcare_id)
  user = healthcare.username

  context = {
    'healthcare': healthcare,
    'user': user,
  }

  return render(request, 'healthcare_settings.html', context)

@login_required(login_url='/healthcare/login/')
@user_passes_test(lambda u: u.is_healthcare, login_url='/healthcare/login/')
def healthcare_edit_settings(request, healthcare_id):
  healthcare = healthcare_does_not_exists(healthcare_id)
  user = healthcare.username
  form = UserEditForm(request.POST or None, instance=user)

  if request.method == 'POST':
    if form.is_valid():
      user.save()
      return redirect('healthcare_settings', healthcare_id=healthcare_id)
    else:
      context = {
        'form': form,
        'healthcare': healthcare,
        'user': user,
      }
      return render(request, 'healthcare_edit_settings.html', context)

  context = {
    'form': form,
    'healthcare': healthcare,
    'user': user,
  }

  return render(request, 'healthcare_edit_settings.html', context)

@login_required(login_url='/healthcare/login/')
@user_passes_test(lambda u: u.is_healthcare, login_url='/healthcare/login/')
def healthcare_change_password(request, healthcare_id):
  healthcare = healthcare_does_not_exists(healthcare_id)

  change_password = HealthcareChangePassword.as_view(
    extra_context={'healthcare': healthcare}
  )

  return change_password(request)

@login_required(login_url='/healthcare/login/')
@user_passes_test(lambda u: u.is_healthcare, login_url='/healthcare/login/')
def healthcare_change_password_complete(request, healthcare_id):
  healthcare = healthcare_does_not_exists(healthcare_id)

  change_password_complete = HealthcareChangePasswordComplete.as_view(
    extra_context={'healthcare': healthcare}
  )

  return change_password_complete(request)

@login_required(login_url='/healthcare/login/')
@user_passes_test(lambda u: u.is_healthcare, login_url='/healthcare/login/')
def healthcare_dashboard(request, healthcare_id):
  healthcare = healthcare_does_not_exists(healthcare_id)

  context = {
    'healthcare': healthcare,
  }

  return render(request, 'healthcare_dashboard.html', context)

##########################################
############ Helper Functions ############
##########################################

def healthcare_does_not_exists(healthcare_id):
  """
  Redirects to login if healthcare_id is invalid
  """
  try:
    return Healthcare.objects.get(id=healthcare_id)
  except Healthcare.DoesNotExist:
    redirect('healthcare_login')
