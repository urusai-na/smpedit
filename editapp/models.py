from django.db import models

class Entry(models.Model):
  title = models.CharField(
    max_length=100,
    unique=True
  )
  text = models.TextField(
    null=True
  )
  
  @classmethod
  def get_full_name(cls):
    return '.'.join((__name__, cls.__name__))
