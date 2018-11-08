# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
	user = models.OneToOneField(User)
	cardID = models.CharField(max_length=20, default=None, null=True)

	def __str__(self):
		try:
			return self.user.username
		except:
			return "UserProfile has No User instance"

