from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect

from core.models import Healthcare

@login_required(login_url='/healthcare/login/')
@user_passes_test(lambda u: u.is_healthcare, login_url='/healthcare/login/')
def show_all_patients(request, healthcare_id):
  
  List all patients the healthcare professional has
  
  healthcare = healthcare_does_not_exists(healthcare_id)

  patients = healthcare.patients.all()

  context = {
    'healthcare': healthcare,
    'patients': patients
  }

  return render(request, 'show_all_patients.html', context)

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
