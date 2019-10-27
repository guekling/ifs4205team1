from django.shortcuts import redirect
from core.models import Researcher

### Helper functions related to researcher e.g. login & anonymisation

STATUS_OK = 1
STATUS_ERROR = 0

AGE_NAME = "age"
POSTALCODE_NAME = "postalcode"
DATE_NAME = "date"

COMBI_AGE_EXACT = 'A'
COMBI_AGE_DECADE = 'D'
COMBI_AGE_ALL = '*'
COMBI_POSTALCODE_EXACT = 'P'
COMBI_POSTALCODE_SECTOR = 'XX'
COMBI_POSTALCODE_ALL = '*'
COMBI_DATE_LM = 'LM'
COMBI_DATE_LY = 'LY'
COMBI_DATE_ALL = '*'

QI_COMBI = {
	##### Uncomment for final code #####
	# 11: { # L1_1
	# 	AGE_NAME: COMBI_AGE_EXACT,
	# 	POSTALCODE_NAME: COMBI_POSTALCODE_EXACT,
	# 	DATE_NAME: COMBI_DATE_LM
	# },

	# 21: {
	# 	AGE_NAME: COMBI_AGE_DECADE,
	# 	POSTALCODE_NAME: COMBI_POSTALCODE_EXACT,
	# 	DATE_NAME: COMBI_DATE_LM
	# },

	# 22: {
	# 	AGE_NAME: COMBI_AGE_EXACT,
	# 	POSTALCODE_NAME: COMBI_POSTALCODE_SECTOR,
	# 	DATE_NAME: COMBI_DATE_LM
	# },

	# 23: {
	# 	AGE_NAME: COMBI_AGE_EXACT,
	# 	POSTALCODE_NAME: COMBI_POSTALCODE_EXACT,
	# 	DATE_NAME: COMBI_DATE_LY
	# },

	# 31: {
	# 	AGE_NAME: COMBI_AGE_ALL,
	# 	POSTALCODE_NAME: COMBI_POSTALCODE_EXACT,
	# 	DATE_NAME: COMBI_DATE_LM
	# },

	32: {
		AGE_NAME: COMBI_AGE_DECADE,
		POSTALCODE_NAME: COMBI_POSTALCODE_SECTOR,
		DATE_NAME: COMBI_DATE_LM
	},

	33: {
		AGE_NAME: COMBI_AGE_DECADE,
		POSTALCODE_NAME: COMBI_POSTALCODE_EXACT,
		DATE_NAME: COMBI_DATE_LY
	},

	34: {
		AGE_NAME: COMBI_AGE_EXACT,
		POSTALCODE_NAME: COMBI_POSTALCODE_ALL,
		DATE_NAME: COMBI_DATE_LM 
	},

	35: {
		AGE_NAME: COMBI_AGE_EXACT,
		POSTALCODE_NAME: COMBI_POSTALCODE_SECTOR,
		DATE_NAME: COMBI_DATE_LY
	},

	36: {
		AGE_NAME: COMBI_AGE_EXACT,
		POSTALCODE_NAME: COMBI_POSTALCODE_EXACT,
		DATE_NAME: COMBI_DATE_ALL
	},

	41: {
		AGE_NAME: COMBI_AGE_ALL,
		POSTALCODE_NAME: COMBI_POSTALCODE_SECTOR,
		DATE_NAME: COMBI_DATE_LM
	},

	42: {
		AGE_NAME: COMBI_AGE_ALL,
		POSTALCODE_NAME: COMBI_POSTALCODE_EXACT,
		DATE_NAME: COMBI_DATE_LY
	},

	43: {
		AGE_NAME: COMBI_AGE_DECADE,
		POSTALCODE_NAME: COMBI_POSTALCODE_ALL,
		DATE_NAME: COMBI_DATE_LM
	},

	44: {
		AGE_NAME: COMBI_AGE_DECADE,
		POSTALCODE_NAME: COMBI_POSTALCODE_SECTOR,
		DATE_NAME: COMBI_DATE_LY
	},

	45: {
		AGE_NAME: COMBI_AGE_DECADE,
		POSTALCODE_NAME: COMBI_POSTALCODE_EXACT,
		DATE_NAME: COMBI_DATE_ALL
	},

	46: {
		AGE_NAME: COMBI_AGE_EXACT,
		POSTALCODE_NAME: COMBI_POSTALCODE_ALL,
		DATE_NAME: COMBI_DATE_LY
	},

	47: {
		AGE_NAME: COMBI_AGE_EXACT,
		POSTALCODE_NAME: COMBI_POSTALCODE_SECTOR,
		DATE_NAME: COMBI_DATE_ALL
	},

	51: {
		AGE_NAME: COMBI_AGE_ALL,
		POSTALCODE_NAME: COMBI_POSTALCODE_ALL,
		DATE_NAME: COMBI_DATE_LM
	},

	52: {
		AGE_NAME: COMBI_AGE_ALL,
		POSTALCODE_NAME: COMBI_POSTALCODE_SECTOR,
		DATE_NAME: COMBI_DATE_LY
	},

	53: {
		AGE_NAME: COMBI_AGE_ALL,
		POSTALCODE_NAME: COMBI_POSTALCODE_EXACT,
		DATE_NAME: COMBI_DATE_ALL
	},

	54: {
		AGE_NAME: COMBI_AGE_DECADE,
		POSTALCODE_NAME: COMBI_POSTALCODE_ALL,
		DATE_NAME: COMBI_DATE_LY
	},

	55: {
		AGE_NAME: COMBI_AGE_DECADE,
		POSTALCODE_NAME: COMBI_POSTALCODE_SECTOR,
		DATE_NAME: COMBI_DATE_ALL
	},

	56: {
		AGE_NAME: COMBI_AGE_EXACT,
		POSTALCODE_NAME: COMBI_POSTALCODE_ALL,
		DATE_NAME: COMBI_DATE_ALL
	},

	61: {
		AGE_NAME: COMBI_AGE_ALL,
		POSTALCODE_NAME: COMBI_POSTALCODE_ALL,
		DATE_NAME: COMBI_DATE_LY
	},

	62: {
		AGE_NAME: COMBI_AGE_ALL,
		POSTALCODE_NAME: COMBI_POSTALCODE_SECTOR,
		DATE_NAME: COMBI_DATE_ALL
	},

	63: {
		AGE_NAME: COMBI_AGE_DECADE,
		POSTALCODE_NAME: COMBI_POSTALCODE_ALL,
		DATE_NAME: COMBI_DATE_ALL
	},

	71: {
		AGE_NAME: COMBI_AGE_ALL,
		POSTALCODE_NAME: COMBI_POSTALCODE_ALL,
		DATE_NAME: COMBI_DATE_ALL
	}
}

def generalise_age_decade(age):
	ages = []

	if 0 <= age <= 10:
		ages = list(range(0, 11))
		return ages

	if 11 <= age <= 20:
		ages = list(range(11, 21))
		return ages

	if 21 <= age <= 30:
		ages = list(range(21, 31))
		return ages

	if 31 <= age <= 40:
		ages = list(range(31, 41))
		return ages

	if 41 <= age <= 50:
		ages = list(range(41, 51))
		return ages

	if 51 <= age <= 60:
		ages = list(range(51, 61))
		return ages

	if 61 <= age <= 70:
		ages = list(range(61, 71))
		return ages

	if 71 <= age <= 80:
		ages = list(range(71, 81))
		return ages

	if 81 <= age <= 90:
		ages = list(range(81, 91))
		return ages

	if 91 <= age <= 100:
		ages = list(range(91, 101))
		return ages

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

def check_researcher_exists(researcher_id):
	"""
	Redirects to login if researcher_id is invalid
	"""
	try:
		return Researcher.objects.get(id=researcher_id)
	except Researcher.DoesNotExist:
		redirect('researcher_login')