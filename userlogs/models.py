import uuid

from django.db import models
from core.models import User

class Logs(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	type = models.CharField(max_length=64)
	timestamp = models.DateTimeField(auto_now=True)
	user_id = models.ForeignKey( # many logs related to one user
		User,
		on_delete=models.PROTECT,
		related_name='logs_user'
	)
	details = models.CharField(max_length=128)