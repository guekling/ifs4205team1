from django.db import models

class QiInfo(models.Model):
	combi_age = models.CharField(max_length=3)
	combi_postalcode = models.CharField(max_length=2)
	combi_date = models.CharField(max_length=2)
	k_value = models.PositiveIntegerField() # max digits = 2
	suppression_rate = models.DecimalField(max_digits=4, decimal_places=2)

	def get_combi_age(self):
		return self.combi_age

	def get_combi_postalcode(self):
		return self.combi_postalcode

	def get_combi_date(self):
		return self.combi_date

	def get_k_value(self):
		return self.k_value

	def get_suppression_rate(self):
		return self.suppression_rate

class SafeUsers(models.Model): 
	uid = models.PositiveIntegerField(primary_key=True, unique=True)
	age = models.CharField(max_length=8)
	postalcode = models.CharField(max_length=6)

	def get_uid(self):
		return self.uid

	def get_age(self):
		return self.age

	def get_postalcode(self):
		return self.postalcode

	def get_diagnosis(self):
		return self.safediagnosis_set.all()

	def get_bp_readings(self):
		return self.safereadings_set.filter(type="Blood Pressure")

	def get_hr_readings(self):
		return self.safereadings_set.filter(type="Heart Rate")

	def get_temp_readings(self):
		return self.safereadings_set.filter(type="Temperature")

	def get_cancer_images(self):
		return self.safeimages_set.filter(type="Cancer")

	def get_mri_images(self):
		return self.safeimages_set.filter(type="MRI")

	def get_ultrasound_images(self):
		return self.safeimages_set.filter(type="Ultrasound")

	def get_xray_images(self):
		return self.safeimages_set.filter(type="Xray")

	def get_gastroscope_videos(self):
		return self.safevideos_set.filter(type="Gastroscope")

	def get_gait_videos(self):
		return self.safevideos_set.filter(type="Gait")

class SafeDiagnosis(models.Model):
	uid = models.ForeignKey(
		SafeUsers,
		on_delete=models.CASCADE,
	)
	value = models.CharField(max_length=64)

class SafeReadings(models.Model):
	uid = models.ForeignKey(
		SafeUsers,
		on_delete=models.CASCADE,
	)
	type = models.CharField(max_length=64)
	value = models.CharField(max_length=16)

class SafeImages(models.Model):
	uid = models.ForeignKey(
		SafeUsers,
		on_delete=models.CASCADE,
	)
	type = models.CharField(max_length=64)
	value = models.CharField(max_length=128)

class SafeVideos(models.Model):
	uid = models.ForeignKey(
		SafeUsers,
		on_delete=models.CASCADE,
	)
	type = models.CharField(max_length=64)
	value = models.CharField(max_length=128)