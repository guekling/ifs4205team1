from __future__ import division
from django.utils import timezone
from datetime import timedelta
import pytz
import os

from core.models import Patient, User
from patientrecords.models import Diagnosis, Readings, Images, Videos
from researcherquery.models import QiInfo, SafeUsers, SafeDiagnosis, SafeReadings, SafeImages, SafeVideos
from adminlogin.anonymise_helper import *

def anonymise_and_store():
	k_value = 3

	# Step 1: For each QI combi e.g. (A, P, LM)
	for key in QI_COMBI:
		print(key)
		print(QI_COMBI[key])
		# Step 2: For each set of unique QIs
		# Step 2a: Retrieve each set of unique QIs from DB
		# Step 2b: Loop the list

		# Get all users including non-patients with distinct pair of age & postalcode
		# Only get 1st entry of distinct pairs
		# Will not get all patients if each set of distinct pair has multiple rows
		unique_entries = User.objects.distinct('age', 'postalcode').order_by('age', 'postalcode')

		patients = Patient.objects.all()
		total_patients = patients.count()

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

				# After for loop:
				# users = all patients with at least 1 record in current set of unique QIs
				# users_copy = all patients with or without at least 1 record in current set of unique QIs

				# Step 7: Check if # of patients left >= k
				# Step 7a: If (patients_left >= k), continue to next set of unique QIs value (same QI combi)
				# Step 7b: Else, suppress all patients with this set of unique QIs
				patients_left = users.count()

				# patients = all patients

				if not (patients_left >= k_value):
					for user in users_copy:
						patients = patients.exclude(username=user.username)

				# After if:
				# patients = all patients that satisfy at least k patients in current set of unique QIs

		# Step 8: Compute suppression rate
		# Step 8a: If suppression rate <= 0.1, done (exit loop and store this QIs combi in SAFE DB)
		# Step 8b: Else, continue to next QIs combi
		total_patients_left = patients.count()
		suppression_rate = ((total_patients - total_patients_left) / total_patients) * 100

		# print("TOTAL PATIENT")
		# print(total_patients)
		# print(total_patients_left)
		# print(suppression_rate)

		if suppression_rate <= 10.0:
			# Step 9: Store anonymised records into SAFE DB
			store_qi_combi(QI_COMBI[key], k_value, suppression_rate)
			store_anonymised_records(QI_COMBI[key], patients)
			break

def store_qi_combi(qi_combi, k_value, suppression_rate):
	combi_age = qi_combi[AGE_NAME]
	combi_postalcode = qi_combi[POSTALCODE_NAME]
	combi_date = qi_combi[DATE_NAME]

	# print("STORE_QI_COMBI")

	# Remove all data from table if not empty
	qiinfo_data = QiInfo.objects.all()
	if qiinfo_data.count() != 0:
		QiInfo.objects.all().delete()

	QiInfo.objects.create(combi_age=combi_age, combi_postalcode=combi_postalcode, combi_date=combi_date, k_value=k_value, suppression_rate=suppression_rate)

	# print("DONE_SAVING_QI_COMBI")

def store_anonymised_records(qi_combi, patients):
	# Remove all data from tables if not empty
	safediagnosis_data = SafeDiagnosis.objects.all()
	if safediagnosis_data.count() != 0:
		SafeDiagnosis.objects.all().delete()

	safereadings_data = SafeReadings.objects.all()
	if safereadings_data.count() != 0:
		SafeReadings.objects.all().delete()

	safeimages_data = SafeImages.objects.all()
	if safeimages_data.count() != 0:
		SafeImages.objects.all().delete()

	safevideos_data = SafeVideos.objects.all()
	if safevideos_data.count() != 0:
		SafeVideos.objects.all().delete()

	safeusers_data = SafeUsers.objects.all()
	if safeusers_data.count() != 0:
		SafeUsers.objects.all().delete()

	# print("STORE_ANONYMISED_RECORDS")

	for patient in patients:
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

		safeusers_obj = SafeUsers.objects.create(uid=user.uid, age=user.age, postalcode=user.postalcode)

		# Get all diagnosis associated with current patient in range
		diagnosis = get_records_in_range(qi_combi[DATE_NAME], DIAGNOSIS_NAME, patient)
		for diag in diagnosis:
			safediagnosis_obj = SafeDiagnosis.objects.create(uid=safeusers_obj, value=diag.title)

		# Get all readings associated with current patient in range
		readings = get_records_in_range(qi_combi[DATE_NAME], READINGS_NAME, patient)
		for reading in readings:
			safereadings_obj = SafeReadings.objects.create(uid=safeusers_obj, type=reading.type, value=reading.data)
			# print(safereadings_obj.id)

		# Get all images associated with current patient in range
		images = get_records_in_range(qi_combi[DATE_NAME], IMAGES_NAME, patient)
		for img in images:
			filename = os.path.basename(img.data.name)
			safeimages_obj = SafeImages.objects.create(uid=safeusers_obj, type=img.type, value=filename)

		# Get all videos associated with current patient in range
		videos = get_records_in_range(qi_combi[DATE_NAME], VIDEOS_NAME, patient)
		for vid in videos:
			filename = os.path.basename(vid.data.name)
			safevideos_obj = SafeVideos.objects.create(uid=safeusers_obj, type=vid.type, value=filename)

	# print("DONE_SAVING_RECORDS")

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

def generalise_date(combi_date):
	duration = timezone.now()

	if combi_date == COMBI_DATE_LM:
		duration = duration - timedelta(days=30)

	if combi_date == COMBI_DATE_LY:
		duration = duration - timedelta(days=365)

	return duration

# Generalise date and check if at least one record exists for each patient
def generalise_date_and_check_record_exists(combi_date, patient):
	duration = generalise_date(combi_date)

	if combi_date == COMBI_DATE_LM or combi_date == COMBI_DATE_LY: # LM or LY
		diagnosis = patient.diagnosis_patient.filter(time_start__gte=duration)
		if diagnosis.count() != 0:
			return True

		readings = patient.readings_patient.filter(type__in=['Blood Pressure', 'Heart Rate', 'Temperature'], timestamp__gte=duration)
		if readings.count() != 0:
			return True

		images = patient.images_patient.filter(type__in=['Cancer', 'MRI', 'Ultrasound', 'Xray'], timestamp__gte=duration)
		if images.count() != 0:
			return True

		videos = patient.videos_patient.filter(type__in=['Gastroscope', 'Gait'], timestamp__gte=duration)
		if videos.count() != 0:
			return True

		return False
	else:
		diagnosis = patient.diagnosis_patient.all()
		if diagnosis.count() != 0:
			return True

		readings = patient.readings_patient.filter(type__in=['Blood Pressure', 'Heart Rate', 'Temperature'])
		if readings.count() != 0:
			return True

		images = patient.images_patient.filter(type__in=['Cancer', 'MRI', 'Ultrasound', 'Xray'])
		if images.count() != 0:
			return True

		videos = patient.videos_patient.filter(type__in=['Gastroscope', 'Gait'])
		if videos.count() != 0:
			return True

		return False

# Only get the 10 record types
def get_records_in_range(combi_date, recordtype, patient):
	duration = generalise_date(combi_date)

	if combi_date == COMBI_DATE_LM or combi_date == COMBI_DATE_LY: # LM or LY
		if recordtype == DIAGNOSIS_NAME:
			diagnosis = patient.diagnosis_patient.filter(time_start__gte=duration)
			return diagnosis

		if recordtype == READINGS_NAME:
			readings = patient.readings_patient.filter(type__in=['Blood Pressure', 'Heart Rate', 'Temperature'], timestamp__gte=duration)
			return readings

		if recordtype == IMAGES_NAME:
			images = patient.images_patient.filter(type__in=['Cancer', 'MRI', 'Ultrasound', 'Xray'], timestamp__gte=duration)
			return images

		if recordtype == VIDEOS_NAME:
			videos = patient.videos_patient.filter(type__in=['Gastroscope', 'Gait'], timestamp__gte=duration)
			return videos
	else:
		if recordtype == DIAGNOSIS_NAME:
			diagnosis = patient.diagnosis_patient.all()
			return diagnosis

		if recordtype == READINGS_NAME:
			readings = patient.readings_patient.filter(type__in=['Blood Pressure', 'Heart Rate', 'Temperature'])
			return readings

		if recordtype == IMAGES_NAME:
			images = patient.images_patient.filter(type__in=['Cancer', 'MRI', 'Ultrasound', 'Xray'])
			return images

		if recordtype == VIDEOS_NAME:
			videos = patient.videos_patient.filter(type__in=['Gastroscope', 'Gait'])
			return videos

DIAGNOSIS_NAME = 'diagnosis'
READINGS_NAME = 'readings'
IMAGES_NAME = 'images'
VIDEOS_NAME = 'videos'