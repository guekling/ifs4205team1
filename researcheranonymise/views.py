from __future__ import division
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import timedelta
import pytz
from core.models import Researcher, Patient, User # Change to admin
from patientrecords.models import Diagnosis, Readings, Images, Videos # Production DB
from researcherquery.models import QiInfo, SafeUsers, SafeDiagnosis, SafeReadings, SafeImages, SafeVideos # SAFE DB
from userlogs.models import Logs
from researcherquery.helper import *

# Change to admin login
@login_required(login_url='/researcher/login/')
@user_passes_test(lambda u: u.is_researcher(), login_url='/researcher/login/')
def anonymise_records(request, researcher_id): # Change to admin_id
	# Checks if logged in admin has the same id as in the URL
	if (request.user.researcher_username.id != researcher_id):
		Logs.objects.create(type='READ', user_id=request.user.uid, interface='ADMIN', status=STATUS_ERROR, details='[Anonymise Records] Logged in user does not match ID in URL. URL ID: ' + str(researcher_id))
		return redirect('researcher_login')

	researcher = check_researcher_exists(researcher_id)
	user = researcher.username

	# the action has not gone through QR verification
	if len(user.sub_id_hash) > 0:
		return redirect('researcher_login')

	context = {
		'researcher': researcher
	}

	# Check if GET (first load) or POST (subsequent load)
	if request.method == 'POST':
		# Pre-Process DB
		anonymise()

		Logs.objects.create(type='UPDATE', user_id=user.uid, interface='ADMIN', status=STATUS_OK, details='Anonymise Records')

		return render(request, 'anonymise_records.html', context)

	# GET - First load
	else:
		return render(request, 'anonymise_records.html', context)

##########################################
############ Helper Functions ############
##########################################

def anonymise():
	k_value = 3
	patients = Patient.objects.all()
	total_patients = patients.count()

	# Step 1: For each QI combi e.g. (A, P, LM)
	for key in QI_COMBI:
		# Step 2: For each set of unique QIs
		# Step 2a: Retrieve each set of unique QIs from DB
		# Step 2b: Loop the list

		# Get all users including non-patients with distinct pair of age & postalcode
		# Only get 1st entry of distinct pairs
		# Will not get all patients if each set of distinct pair has multiple rows
		unique_entries = User.objects.distinct('age', 'postalcode').order_by('age', 'postalcode')

		for unique_entry in unique_entries:
			if unique_entry.is_patient():
				unique_qi_age = unique_entry.age
				unique_qi_postalcode = unique_entry.postalcode

				print(unique_qi_age)
				print(unique_qi_postalcode)

				# Step 3: Generalise QIs (age & postalcode) based on QIs combi
				# Step 4: Get all users including non-patients with current set of unique QIs (set QIs as filter)
				users = generalise_and_get_users(QI_COMBI[key], unique_entry)
				users_copy = users

				for user in users:
					if user.is_patient():
						patient = user.patient_username

						# Step 5: Generalise date
						# Step 6: Check if patient has at least 1 record (readings) within the combi_date (LM, LY or *)
						# Step 6a: If exists at least 1 record, continue (keep patient)
						# Step 6b: Else, remove patient from list then continue
						record_exists = generalise_date_and_check_record_exists(QI_COMBI[key][DATE_NAME], patient)

						if not record_exists:
							# Remove patient from list
							users = users.exclude(username=user.username)

					else:
						users = users.exclude(username=user.username)
						users_copy = users_copy.exclude(username=user.username)

				# After this for loop:
				# users = all patients with at least 1 record in current set of unique QIs
				# users_copy = all patients with or without at least 1 record in current set of unique QIs

				# Step 7: Check if # of patients left >= k
				# Step 7a: If (patients_left >= k), continue to next set of unique QIs value (same QI combi)
				# Step 7b: Else, suppress all patients with this set of unique QIs
				patients_left = users.count()

				# patients = all patients

				if not (patients_left >= k_value):
					for user in users_copy:
						print("LINE 145")
						patients = patients.exclude(username=user.username)

				# After this if:
				# patients = all patients that satisfy at least k patients in current set of unique QIs

		# Step 8: Compute suppression rate
		# Step 8a: If suppression rate <= 0.1, done (exit loop and store this QIs combi in SAFE DB)
		# Step 8b: Else, continue to next QIs combi
		total_patients_left = patients.count()
		suppression_rate = ((total_patients - total_patients_left) / total_patients) * 100

		print("TOTAL PATIENT")
		print(total_patients)
		print(total_patients_left) #COMPARE WITH THIS
		print(suppression_rate)

		if suppression_rate <= 10.0:
			# Step 9: Store anonymised records into SAFE DB
			store_qi_combi(QI_COMBI[key], k_value, suppression_rate)
			store_anonymised_records(QI_COMBI[key], patients)
			break

def store_qi_combi(qi_combi, k_value, suppression_rate):
	combi_age = qi_combi[AGE_NAME]
	combi_postalcode = qi_combi[POSTALCODE_NAME]
	combi_date = qi_combi[DATE_NAME]

	print("STORE_QI_COMBI")

	# Remove all data from table if not empty
	qiinfo_data = QiInfo.objects.all()
	if qiinfo_data.count() != 0:
		QiInfo.objects.all().delete()

	qiinfo_obj = QiInfo(combi_age=combi_age, combi_postalcode=combi_postalcode, combi_date=combi_date, k_value=k_value, suppression_rate=suppression_rate)
	qiinfo_obj.save()

	print("DONE_SAVING_QI_COMBI")

	# print(qiinfo_obj.id)

def store_anonymised_records(qi_combi, patients):
	# Remove all data from tables if not empty
	safereadings_data = SafeReadings.objects.all()
	if safereadings_data.count() != 0:
		SafeReadings.objects.all().delete()

	safeusers_data = SafeUsers.objects.all()
	if safeusers_data.count() != 0:
		SafeUsers.objects.all().delete()

	print("STORE_ANONYMISED_RECORDS")

	uid = 0
	for patient in patients:
		uid += 1
		user = User.objects.get(username=patient.username)

		# Convert age & postalcode based on current QI combi
		if qi_combi[AGE_NAME] == COMBI_AGE_DECADE:
			user.age = map_age_to_decade(user.age)
		if qi_combi[AGE_NAME] == COMBI_AGE_ALL:
			user.age = '*'

		if qi_combi[POSTALCODE_NAME] == COMBI_POSTALCODE_SECTOR:
			user.postalcode = user.postalcode[:2] + 'XXXX'
		if qi_combi[POSTALCODE_NAME] == COMBI_POSTALCODE_ALL:
			user.postalcode = '*'

		safeusers_obj = SafeUsers(uid=uid, age=user.age, postalcode=user.postalcode)
		safeusers_obj.save()

		# print(safeusers_obj.uid)

		# Get all readings associated with current patient
		readings = patient.readings_patient.all()
		for reading in readings:
			safereadings_obj = SafeReadings(uid=safeusers_obj, type=reading.type, value=reading.data)
			safereadings_obj.save()

			# print(safereadings_obj.id)

	print("DONE_SAVING_RECORDS")


def generalise_and_get_users(qi_combi, user):
	combi_age = qi_combi[AGE_NAME]
	combi_postalcode = qi_combi[POSTALCODE_NAME]

	if combi_age == COMBI_AGE_EXACT and combi_postalcode == COMBI_POSTALCODE_EXACT:
		users = User.objects.filter(age=user.age, postalcode=user.postalcode).order_by('age', 'postalcode')
		return users

	if combi_age == COMBI_AGE_EXACT and combi_postalcode == COMBI_POSTALCODE_SECTOR:
		postalcode = str(user.postalcode)
		postalcode = postalcode[:2]
		users = User.objects.filter(age=user.age, postalcode__startswith=postalcode).order_by('age', 'postalcode')		
		return users

	if combi_age == COMBI_AGE_EXACT and combi_postalcode == COMBI_POSTALCODE_ALL:
		users = User.objects.filter(age=user.age).order_by('age', 'postalcode')
		return users

	if combi_age == COMBI_AGE_DECADE and combi_postalcode == COMBI_POSTALCODE_EXACT:
		ages = generalise_age_decade(user.age)
		users = User.objects.filter(age__in=ages, postalcode=user.postalcode).order_by('age', 'postalcode')		
		return users

	if combi_age == COMBI_AGE_DECADE and combi_postalcode == COMBI_POSTALCODE_SECTOR:
		ages = generalise_age_decade(user.age)
		postalcode = str(user.postalcode)
		postalcode = postalcode[:2]
		users = User.objects.filter(age__in=ages, postalcode__startswith=postalcode).order_by('age', 'postalcode')
		return users

	if combi_age == COMBI_AGE_DECADE and combi_postalcode == COMBI_POSTALCODE_ALL:
		ages = generalise_age_decade(user.age)
		users = User.objects.filter(age__in=ages).order_by('age', 'postalcode')
		return users

	if combi_age == COMBI_AGE_ALL and combi_postalcode == COMBI_POSTALCODE_EXACT:
		users = User.objects.filter(postalcode=user.postalcode).order_by('age', 'postalcode')
		return users

	if combi_age == COMBI_AGE_ALL and combi_postalcode == COMBI_POSTALCODE_SECTOR:
		postalcode = str(user.postalcode)
		postalcode = postalcode[:2]
		users = User.objects.filter(postalcode__startswith=postalcode).order_by('age', 'postalcode')
		return users

	if combi_age == COMBI_AGE_ALL and combi_postalcode == COMBI_POSTALCODE_ALL:
		users = User.objects.all().order_by('age', 'postalcode')
		return users

def generalise_date_and_check_record_exists(combi_date, patient):
	duration = timezone.now()

	if combi_date == COMBI_DATE_LM:
		duration = duration - timedelta(days=30)

	if combi_date == COMBI_DATE_LY:
		duration = duration - timedelta(days=365)

	if combi_date == COMBI_DATE_LM or combi_date == COMBI_DATE_LY: # LM or LY
		bp_readings = patient.readings_patient.filter(type='Blood Pressure', timestamp__gte=duration)
		hr_readings = patient.readings_patient.filter(type='Heart Rate', timestamp__gte=duration)
		temp_readings = patient.readings_patient.filter(type='Temperature', timestamp__gte=duration)

		if bp_readings.count() != 0 or hr_readings.count() != 0 or temp_readings.count() != 0:
			return True
		return False

	else:
		bp_readings = patient.readings_patient.filter(type='Blood Pressure')
		hr_readings = patient.readings_patient.filter(type='Heart Rate')
		temp_readings = patient.readings_patient.filter(type='Temperature')

		if bp_readings.count() != 0 or hr_readings.count() != 0 or temp_readings.count() != 0:
			return True
		return False