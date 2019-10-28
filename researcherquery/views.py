from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core import serializers
from core.models import User, Researcher
from researcherquery.models import QiInfo, SafeUsers, SafeDiagnosis, SafeReadings, SafeImages, SafeVideos
from userlogs.models import Logs
from researcherquery.forms import SearchRecordsForm
import datetime
import csv
import xlwt
import json

@login_required(login_url='/researcher/login/')
@user_passes_test(lambda u: u.is_researcher(), login_url='/researcher/login/')
def search_records(request, researcher_id):
	# Checks if logged in researcher has the same id as in the URL
	if (request.user.researcher_username.id != researcher_id):
		Logs.objects.create(type='READ', user_id=request.user.uid, interface='RESEARCHER', status=STATUS_ERROR, details='[Search Records] Logged in user does not match ID in URL. URL ID: ' + str(researcher_id))
		return redirect('researcher_login')

	researcher = check_researcher_exists(researcher_id)
	user = researcher.username

	# the action has not gone through QR verification
	if len(user.sub_id_hash) > 0:
		return redirect('researcher_login')

	today_date = datetime.datetime.now().strftime("%Y-%m-%d")
	reset_recordtypes_choices_checkbox()
	submitted = False

	# Check if GET (first load) or POST (subsequent load)
	if request.method == 'POST':
		set_recordtypes_perm_if_empty(researcher)
		form = SearchRecordsForm(request.POST, tday=today_date, perm=RECORD_TYPES_PERMISSION)

		if form.is_valid():
			# Get values from POST request
			ages = request.POST.getlist('age')
			postalcode1 = request.POST.get('postalcode1')
			postalcode2 = request.POST.get('postalcode2')
			postalcode3 = request.POST.get('postalcode3')
			recordtypes = request.POST.getlist('recordtypes')
			searched = request.POST.get('btn_search')

			if searched == "Search": # btn is clicked
				submitted = True

			# Get current QI combi from DB (always 1st entry as only store 1)
			qiinfo = QiInfo.objects.all().first()
			combi_age = qiinfo.get_combi_age()
			combi_postalcode = qiinfo.get_combi_postalcode()
			combi_date = qiinfo.get_combi_date()

			# Process the QIs & Record Types
			##### Add in exception checking codes
			postalcodes = []
			if postalcode1:
				postalcodes.append(postalcode1)
			if postalcode2:
				postalcodes.append(postalcode2)
			if postalcode3:
				postalcodes.append(postalcode3)

			users = process_age_postalcode(combi_age, combi_postalcode, ages, postalcodes)
			users_list = list(users)
			request.session['users_list'] = serializers.serialize("json", users_list)
			process_recordtypes(recordtypes)

			Logs.objects.create(type='READ', user_id=user.uid, interface='RESEARCHER', status=STATUS_OK, details='Search Records')

			context = {
				'form': form,
				'researcher': researcher,
				'qiinfo': qiinfo,
				'users': users,
				'count': users.count(),
				'date': process_date(combi_date),
				'submitted': submitted,
				DIAGNOSIS_NAME: RECORD_TYPES_SELECTED[DIAGNOSIS_NAME],
				BP_READING_NAME: RECORD_TYPES_SELECTED[BP_READING_NAME],
				HR_READING_NAME: RECORD_TYPES_SELECTED[HR_READING_NAME],
				TEMP_READING_NAME: RECORD_TYPES_SELECTED[TEMP_READING_NAME],
				CANCER_IMG_NAME: RECORD_TYPES_SELECTED[CANCER_IMG_NAME],
				MRI_IMG_NAME: RECORD_TYPES_SELECTED[MRI_IMG_NAME],
				ULTRASOUND_IMG_NAME: RECORD_TYPES_SELECTED[ULTRASOUND_IMG_NAME],
				XRAY_IMG_NAME: RECORD_TYPES_SELECTED[XRAY_IMG_NAME],
				GASTROSCOPE_VID_NAME: RECORD_TYPES_SELECTED[GASTROSCOPE_VID_NAME],
				GAIT_VID_NAME: RECORD_TYPES_SELECTED[GAIT_VID_NAME]
			}

			return render(request, 'search_records.html', context)

		# POST - Handle invalid form
		set_recordtypes_perm_if_empty(researcher)
		form = SearchRecordsForm(request.POST, tday=today_date, perm=RECORD_TYPES_PERMISSION)

		context = {
			'form': form,
			'researcher': researcher
		}
		
		return render(request, 'search_records.html', context)

	# GET - First load
	else:
		set_recordtypes_perm_if_empty(researcher)
		form = SearchRecordsForm(tday=today_date, perm=RECORD_TYPES_PERMISSION)

		context = {
			'form': form,
			'researcher': researcher
		}

		return render(request, 'search_records.html', context)

@login_required(login_url='researcher_login')
@user_passes_test(lambda u: u.is_researcher(), login_url='researcher_login')
def download_records_csv(request, researcher_id):
	# Checks if logged in researcher has the same id as in the URL
	if (request.user.researcher_username.id != researcher_id):
		Logs.objects.create(type='READ', user_id=request.user.uid, interface='RESEARCHER', status=STATUS_ERROR, details='[Download Anonymised Records (CSV)] Logged in user does not match ID in URL. URL ID: ' + str(researcher_id))
		return redirect('researcher_login')

	researcher = check_researcher_exists(researcher_id)
	user = researcher.username

	# the action has not gone through QR verification
	if len(user.sub_id_hash) > 0:
		return redirect('researcher_login')

	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="anonymised_records.csv"'

	writer = csv.writer(response)
	writer.writerow(['Patient', 'Age', 'Postal Code', 'Date', 'Diagnosis', 'BP Readings', 'HR Readings', 'TEMP Readings'])

	qiinfo_combi_date = QiInfo.objects.all().first().get_combi_date()
	date = process_date(qiinfo_combi_date)

	users_list = request.session.get('users_list', None)
	safeusers = json.loads(users_list)

	for safeuser in safeusers:
		safeuser_list = []

		uid = safeuser['pk']
		age = safeuser['fields']['age']
		postalcode = safeuser['fields']['postalcode']

		safeuser_list.append(uid)
		safeuser_list.append(age)
		safeuser_list.append(postalcode)
		safeuser_list.append(date)

		safeuser_obj = SafeUsers.objects.get(pk=uid)

		if RECORD_TYPES_SELECTED[DIAGNOSIS_NAME]:
			diagnosis_list = []
			diagnosis_obj = safeuser_obj.get_diagnosis()
			for diag in diagnosis_obj:
				diagnosis_list.append(diag.value)
			safeuser_list.append(str(diagnosis_list))
		else:
			safeuser_list.append('')

		if RECORD_TYPES_SELECTED[BP_READING_NAME]:
			bp_readings_list = []
			bp_reading_obj = safeuser_obj.get_bp_readings()
			for bp_reading in bp_reading_obj:
				bp_readings_list.append(bp_reading.value)
			safeuser_list.append(str(bp_readings_list))
		else:
			safeuser_list.append('')

		
		if RECORD_TYPES_SELECTED[HR_READING_NAME]:
			hr_readings_list = []
			hr_reading_obj = safeuser_obj.get_hr_readings()
			for hr_reading in hr_reading_obj:
				hr_readings_list.append(hr_reading.value)
			safeuser_list.append(str(hr_readings_list))
		else:
			safeuser_list.append('')

		if RECORD_TYPES_SELECTED[TEMP_READING_NAME]:
			temp_readings_list = []
			temp_reading_obj = safeuser_obj.get_temp_readings()
			for temp_reading in temp_reading_obj:
					temp_readings_list.append(temp_reading.value)
			safeuser_list.append(str(temp_readings_list))
		else:
			safeuser_list.append('')

		writer.writerow(safeuser_list)

	Logs.objects.create(type='READ', user_id=user.uid, interface='RESEARCHER', status=STATUS_OK, details='Download Anonymised Records (CSV)')
	return response

@login_required(login_url='researcher_login')
@user_passes_test(lambda u: u.is_researcher(), login_url='researcher_login')
def download_records_xls(request, researcher_id):
	# Checks if logged in researcher has the same id as in the URL
	if (request.user.researcher_username.id != researcher_id):
		Logs.objects.create(type='READ', user_id=request.user.uid, interface='RESEARCHER', status=STATUS_ERROR, details='[Download Anonymised Records (XLS)] Logged in user does not match ID in URL. URL ID: ' + str(researcher_id))
		return redirect('researcher_login')

	researcher = check_researcher_exists(researcher_id)
	user = researcher.username

	# the action has not gone through QR verification
	if len(user.sub_id_hash) > 0:
		return redirect('researcher_login')


	response = HttpResponse(content_type='application/ms-excel')
	response['Content-Disposition'] = 'attachment; filename="anonymised_records.xls"'

	wb = xlwt.Workbook(encoding='utf-8')
	ws = wb.add_sheet('Anonymised Records')

	# Sheet header, first row
	row_num = 0

	font_style = xlwt.XFStyle()
	font_style.font.bold = True

	columns = ['Patient', 'Age', 'Postal Code', 'Date', 'Diagnosis', 'BP Readings', 'HR Readings', 'TEMP Readings']
	for col_num in range(len(columns)):
		ws.write(row_num, col_num, columns[col_num], font_style)

	# Sheet body, remaining rows
	font_style = xlwt.XFStyle()

	qiinfo_combi_date = QiInfo.objects.all().first().get_combi_date()
	date = process_date(qiinfo_combi_date)

	users_list = request.session.get('users_list', None)
	safeusers = json.loads(users_list)

	for safeuser in safeusers:
		row_num += 1

		uid = safeuser['pk']
		age = safeuser['fields']['age']
		postalcode = safeuser['fields']['postalcode']

		ws.write(row_num, 0, uid, font_style)
		ws.write(row_num, 1, age, font_style)
		ws.write(row_num, 2, postalcode, font_style)
		ws.write(row_num, 3, date, font_style)

		safeuser_obj = SafeUsers.objects.get(pk=uid)

		if RECORD_TYPES_SELECTED[DIAGNOSIS_NAME]:
			diagnosis_list = []
			diagnosis_obj = safeuser_obj.get_diagnosis()
			for diag in diagnosis_obj:
				diagnosis_list.append(diag.value)
			ws.write(row_num, 4, str(diagnosis_list), font_style)
		else:
			ws.write(row_num, 4, '', font_style)

		if RECORD_TYPES_SELECTED[BP_READING_NAME]:
			bp_readings_list = []
			bp_reading_obj = safeuser_obj.get_bp_readings()
			for bp_reading in bp_reading_obj:
				bp_readings_list.append(bp_reading.value)
			ws.write(row_num, 5, str(bp_readings_list), font_style)
		else:
			ws.write(row_num, 5, '', font_style)

		
		if RECORD_TYPES_SELECTED[HR_READING_NAME]:
			hr_readings_list = []
			hr_reading_obj = safeuser_obj.get_hr_readings()
			for hr_reading in hr_reading_obj:
				hr_readings_list.append(hr_reading.value)
			ws.write(row_num, 6, str(hr_readings_list), font_style)
		else:
			ws.write(row_num, 6, '', font_style)

		if RECORD_TYPES_SELECTED[TEMP_READING_NAME]:
			temp_readings_list = []
			temp_reading_obj = safeuser_obj.get_temp_readings()
			for temp_reading in temp_reading_obj:
					temp_readings_list.append(temp_reading.value)
			ws.write(row_num, 7, str(temp_readings_list), font_style)
		else:
			ws.write(row_num, 7, '', font_style)

	wb.save(response)
	
	Logs.objects.create(type='READ', user_id=user.uid, interface='RESEARCHER', status=STATUS_OK, details='Download Anonymised Records (XLS)')
	return response

##########################################
############ Helper Functions ############
##########################################

STATUS_OK = 1
STATUS_ERROR = 0

COMBI_AGE_EXACT = 'A'
COMBI_AGE_DECADE = 'D'
COMBI_AGE_ALL = '*'
COMBI_POSTALCODE_EXACT = 'P'
COMBI_POSTALCODE_SECTOR = 'XX'
COMBI_POSTALCODE_ALL = '*'
COMBI_DATE_LM = 'LM'
COMBI_DATE_LY = 'LY'
COMBI_DATE_ALL = '*'

DIAGNOSIS_NAME = 'diagnosis'
BP_READING_NAME = 'bp_reading'
HR_READING_NAME = 'hr_reading'
TEMP_READING_NAME = 'temp_reading'
CANCER_IMG_NAME = 'cancer_img'
MRI_IMG_NAME = 'mri_img'
ULTRASOUND_IMG_NAME = 'ultrasound_img'
XRAY_IMG_NAME = 'xray_img'
GASTROSCOPE_VID_NAME = 'gastroscope_vid'
GAIT_VID_NAME = 'gait_vid'

RECORD_TYPES_NAME_LIST = [
	DIAGNOSIS_NAME,
	BP_READING_NAME,
	HR_READING_NAME,
	TEMP_READING_NAME,
	CANCER_IMG_NAME,
	MRI_IMG_NAME,
	ULTRASOUND_IMG_NAME,
	XRAY_IMG_NAME,
	GASTROSCOPE_VID_NAME,
	GAIT_VID_NAME
]

DIAGNOSIS_DISPLAY_NAME = 'Diagnosis'
BP_READING_DISPLAY_NAME = 'Blood Pressure (BP) Readings'
HR_READING_DISPLAY_NAME = 'Heart Rate (HR) Readings'
TEMP_READING_DISPLAY_NAME = 'Temperature (TEMP) Readings'
CANCER_IMG_DISPLAY_NAME = 'Cancer Images'
MRI_IMG_DISPLAY_NAME = 'MRI Images'
ULTRASOUND_IMG_DISPLAY_NAME = 'Ultrasound Images'
XRAY_IMG_DISPLAY_NAME = 'Xray Images'
GASTROSCOPE_VID_DISPLAY_NAME = 'Gastroscope Videos'
GAIT_VID_DISPLAY_NAME = 'Gait Videos'

# Default display state of all record types in table
RECORD_TYPES_SELECTED = {
	DIAGNOSIS_NAME: False,
	BP_READING_NAME: False,
	HR_READING_NAME: False,
	TEMP_READING_NAME: False,
	CANCER_IMG_NAME: False,
	MRI_IMG_NAME: False,
	ULTRASOUND_IMG_NAME: False,
	XRAY_IMG_NAME: False,
	GASTROSCOPE_VID_NAME: False,
	GAIT_VID_NAME: False
}

RECORD_TYPES_PERMISSION = []

def reset_recordtypes_choices_checkbox():
	for recordtype in RECORD_TYPES_NAME_LIST:
		RECORD_TYPES_SELECTED[recordtype] = False

def set_recordtypes_perm_if_empty(researcher):
	if len(RECORD_TYPES_PERMISSION) == 0:
		get_recordtypes_perm(researcher)

# Get record types perm from DB and append it to list for display as checkbox choices
# Prevents illegal access to record types which the researchers have no perm to
def get_recordtypes_perm(researcher):
	# Add record type to checkbox choices only if perm returns True
	if (researcher.get_diagnosis_perm()):
		RECORD_TYPES_PERMISSION.append((DIAGNOSIS_NAME, DIAGNOSIS_DISPLAY_NAME))

	if (researcher.get_bp_reading_perm()):
		RECORD_TYPES_PERMISSION.append((BP_READING_NAME, BP_READING_DISPLAY_NAME))

	if (researcher.get_hr_reading_perm()):
		RECORD_TYPES_PERMISSION.append((HR_READING_NAME, HR_READING_DISPLAY_NAME))

	if (researcher.get_temp_reading_perm()):
		RECORD_TYPES_PERMISSION.append((TEMP_READING_NAME, TEMP_READING_DISPLAY_NAME))

	if (researcher.get_cancer_img_perm()):
		RECORD_TYPES_PERMISSION.append((CANCER_IMG_NAME, CANCER_IMG_DISPLAY_NAME))

	if (researcher.get_mri_img_perm()):
		RECORD_TYPES_PERMISSION.append((MRI_IMG_NAME, MRI_IMG_DISPLAY_NAME))

	if (researcher.get_ultrasound_img_perm()):
		RECORD_TYPES_PERMISSION.append((ULTRASOUND_IMG_NAME, ULTRASOUND_IMG_DISPLAY_NAME))

	if (researcher.get_xray_img_perm()):
		RECORD_TYPES_PERMISSION.append((XRAY_IMG_NAME, XRAY_IMG_DISPLAY_NAME))

	if (researcher.get_gastroscope_vid_perm()):
		RECORD_TYPES_PERMISSION.append((GASTROSCOPE_VID_NAME, GASTROSCOPE_VID_DISPLAY_NAME))

	if (researcher.get_gait_vid_perm()):
		RECORD_TYPES_PERMISSION.append((GAIT_VID_NAME, GAIT_VID_DISPLAY_NAME))

def process_date(combi_date):
	if combi_date == COMBI_DATE_LM:
		return 'Last Month'

	if combi_date == COMBI_DATE_LY:
		return 'Last Year'

	return COMBI_DATE_ALL

# Process the QIs and retrieve relevant users & records from DB
def process_age_postalcode(combi_age, combi_postalcode, ages, postalcodes):
	if combi_age == COMBI_AGE_EXACT and combi_postalcode == COMBI_POSTALCODE_EXACT:
		# No processing is needed, filter using original lists
		users = SafeUsers.objects.filter(age__in=ages, postalcode__in=postalcodes).order_by('age', 'postalcode')
		return users

	if combi_age == COMBI_AGE_EXACT and combi_postalcode == COMBI_POSTALCODE_SECTOR:
		processed_postalcodes = process_postalcode_sector(postalcodes)
		users = SafeUsers.objects.filter(age__in=ages, postalcode__in=processed_postalcodes).order_by('age', 'postalcode')
		return users

	if combi_age == COMBI_AGE_EXACT and combi_postalcode == COMBI_POSTALCODE_ALL:
		users = SafeUsers.objects.filter(age__in=ages).order_by('age', 'postalcode')
		return users

	if combi_age == COMBI_AGE_DECADE and combi_postalcode == COMBI_POSTALCODE_EXACT:
		processed_ages = process_age_decade(ages)
		users = SafeUsers.objects.filter(age__in=processed_ages, postalcode__in=postalcodes).order_by('age', 'postalcode')
		return users

	if combi_age == COMBI_AGE_DECADE and combi_postalcode == COMBI_POSTALCODE_SECTOR:
		processed_ages = process_age_decade(ages)
		processed_postalcodes = process_postalcode_sector(postalcodes)
		users = SafeUsers.objects.filter(age__in=processed_ages, postalcode__in=processed_postalcodes).order_by('age', 'postalcode')
		return users

	if combi_age == COMBI_AGE_DECADE and combi_postalcode == COMBI_POSTALCODE_ALL:
		processed_ages = process_age_decade(ages)
		users = SafeUsers.objects.filter(age__in=processed_ages).order_by('age', 'postalcode')
		return users

	if combi_age == COMBI_AGE_ALL and combi_postalcode == COMBI_POSTALCODE_EXACT:
		users = SafeUsers.objects.filter(postalcode__in=postalcodes).order_by('age', 'postalcode')
		return users

	if combi_age == COMBI_AGE_ALL and combi_postalcode == COMBI_POSTALCODE_SECTOR:
		processed_postalcodes = process_postalcode_sector(postalcodes)
		users = SafeUsers.objects.filter(postalcode__in=processed_postalcodes).order_by('age', 'postalcode')
		return users

	if combi_age == COMBI_AGE_ALL and combi_postalcode == COMBI_POSTALCODE_ALL:
		users = SafeUsers.objects.all().order_by('age', 'postalcode')
		return users

def process_age_decade(ages):
	processed_ages = []
	for age in ages:
		age_decade = map_age_to_decade(int(age))
		if age_decade not in processed_ages:
			processed_ages.append(age_decade)
	return processed_ages

def map_age_to_decade(age):
	if 0 <= age <= 10:
		return '0-10'

	if 11 <= age <= 20:
		return '11-20'

	if 21 <= age <= 30:
		return '21-30'

	if 31 <= age <= 40:
		return '31-40'

	if 41 <= age <= 50:
		return '41-50'

	if 51 <= age <= 60:
		return '51-60'

	if 61 <= age <= 70:
		return '61-70'

	if 71 <= age <= 80:
		return '71-80'

	if 81 <= age <= 90:
		return '81-90'

	if 91 <= age <= 100:
		return '91-100'

def process_postalcode_sector(postalcodes):
	processed_postalcodes = []
	for postalcode in postalcodes:
		postalcode_sector = postalcode[:2] + 'XXXX'
		if postalcode_sector not in processed_postalcodes:
			processed_postalcodes.append(postalcode_sector)
	return processed_postalcodes

def process_recordtypes(recordtypes):
	# Update state only if selected in checkbox
	# Do not have to validate if researcher has perm for each type as only permitted record types are available as checkbox choices
	for recordtype in recordtypes:
		RECORD_TYPES_SELECTED[recordtype] = True

def check_researcher_exists(researcher_id):
	"""
	Redirects to login if researcher_id is invalid
	"""
	try:
		return Researcher.objects.get(id=researcher_id)
	except Researcher.DoesNotExist:
		redirect('researcher_login')