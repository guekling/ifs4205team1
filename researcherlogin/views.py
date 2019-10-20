from django.shortcuts import render, redirect
from django.template import RequestContext
from django.urls import reverse_lazy

from django.utils.crypto import get_random_string

from django.contrib.auth import (
	REDIRECT_FIELD_NAME, get_user_model, login as auth_login
)

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView

from researcherlogin.forms import UserEditForm, UserQrForm
from core.models import User, Researcher

import hashlib

class ResearcherLogin(LoginView):
	"""
	Custom researcher login view that extends from Django's LoginView
	"""
	form_class = AuthenticationForm
	template_name = 'researcher_login.html'

	def form_valid(self, form):
		"""
		Checks if user is a researcher
		"""
		try:
			researcher = form.get_user().researcher_username
		except Researcher.DoesNotExist:
			researcher = None

		if researcher is not None:
			auth_login(self.request, form.get_user())
			nonce = get_random_string(length=6, allowed_chars=u'abcdefghijklmnopqrstuvwxyz0123456789')
			user = researcher.username
			user.sub_id_hash = nonce # change field
			user.save() # this will update only
			return redirect('researcher_qr', researcher_id=researcher.id)
		else:
			form = AuthenticationForm

			context = {
				'form': form
			}

			return render(self.request, 'researcher_login.html', context)

class ResearcherLogout(LogoutView):
	"""
	Custom researcher logout view that extends from Django's LogoutView
	"""
	next_page = '/researcher/login'

class ResearcherChangePassword(PasswordChangeView):
	"""
	Custom researcher change password view that extends from Django's PasswordChangeView
	"""
	form_class = PasswordChangeForm
	template_name = 'researcher_change_password.html'

	def get_success_url(self):
		user = self.request.user
		url = reverse_lazy('researcher_change_password_complete', kwargs={'researcher_id': user.researcher.id})
		return url

class ResearcherChangePasswordComplete(PasswordChangeDoneView):
	"""
	Custom researcher change password complete view that extends from Django's PasswordChangeDoneView
	"""
	template_name = 'researcher_change_password_complete.html'

@login_required(login_url='/researcher/login/')
@user_passes_test(lambda u: u.is_researcher(), login_url='/researcher/login/')
def researcher_settings(request, researcher_id):
	researcher = researcher_does_not_exists(researcher_id)
	user = researcher.username

	context = {
		'researcher': researcher,
		'user': user
	}

	return render(request, 'researcher_settings.html', context)

@login_required(login_url='/researcher/login/')
@user_passes_test(lambda u: u.is_researcher(), login_url='/researcher/login/')
def researcher_edit_settings(request, researcher_id):
	researcher = researcher_does_not_exists(researcher_id)
	user = researcher.username
	form = UserEditForm(request.POST or None, instance=user)

	if request.method == 'POST':
		if form.is_valid():
			user.save()
			return redirect('researcher_settings', researcher_id=researcher_id)
		else:
			context = {
				'form': form,
				'researcher': researcher,
				'user': user
			}

			return render(request, 'researcher_edit_settings.html', context)

	context = {
		'form': form,
		'researcher': researcher,
		'user': user
	}

	return render(request, 'researcher_edit_settings.html', context)

@login_required(login_url='/researcher/login/')
@user_passes_test(lambda u: u.is_researcher(), login_url='/researcher/login/')
def researcher_change_password(request, researcher_id):
	researcher = researcher_does_not_exists(researcher_id)

	change_password = ResearcherChangePassword.as_view(
		extra_context={'researcher': researcher}
	)

	return change_password(request)

@login_required(login_url='/researcher/login/')
@user_passes_test(lambda u: u.is_researcher(), login_url='/researcher/login/')
def researcher_change_password_complete(request, researcher_id):
	researcher = researcher_does_not_exists(researcher_id)

	change_password_complete = ResearcherChangePasswordComplete.as_view(
			extra_context={'researcher': researcher}
		)

	return change_password_complete(request)

@login_required(login_url='/researcher/login/')
@user_passes_test(lambda u: u.is_researcher(), login_url='/researcher/login/')
def researcher_qr(request, researcher_id):
	researcher = researcher_does_not_exists(researcher_id)
	user = researcher.username
	if len(user.sub_id_hash) > 0:
		nonce = user.sub_id_hash
	else:
		return redirect('researcher_login')

	form = UserQrForm(request.POST or None)

	if form.is_valid():
		cd = form.cleaned_data
		otp = cd.get('otp')
		if otp == '1234':
		# if user.device_id_hash == recovered_value(user.android_id_hash, nonce, otp):
			# given HttpResponse only or render page you need to load on success
			user.sub_id_hash = ""
			user.save()
			return redirect('researcher_dashboard', researcher_id=researcher.id)
		else:
			# if fails, then redirect to custom url/page
			return redirect('researcher_login')

	else:
		context = {
			'form': UserQrForm(),
			'nonce': nonce
		}

		return render(request, 'researcher_qr.html', context)

@login_required(login_url='/researcher/login/')
@user_passes_test(lambda u: u.is_researcher(), login_url='/researcher/login/')
def researcher_dashboard(request, researcher_id):
	researcher = researcher_does_not_exists(researcher_id)

	context = {
		'researcher': researcher
	}

	return render(request, 'researcher_dashboard.html', context)

##########################################
############ Helper Functions ############
##########################################

def researcher_does_not_exists(researcher_id):
	"""
	Redirects to login if researcher_id is invalid
	"""
	try:
		return Researcher.objects.get(id=researcher_id)
	except Researcher.DoesNotExist:
		redirect('researcher_login')

def recovered_value(hash_id, nonce, otp):
	x = hashlib.sha256((hash_id + nonce).encode()).hexdigest()
	xor = '{:x}'.format(int(x[-6:], 16) ^ int(otp, 16))

	return hashlib.sha256((xor).encode()).hexdigest()