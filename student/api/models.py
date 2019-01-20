from django.db import models
from django.contrib.auth.models import User
from api.constants import WEEKDAYS


class Days(models.Model):
    day = models.CharField(max_length=9)

    def save(self, *args, **kwargs):
        weekday = self.day.upper()
        self.day = WEEKDAYS.get(weekday, None)
        assert self.day
        super(Days, self).save(*args, **kwargs)


class Course(models.Model):
    title = models.EmailField(max_length=255, db_index=True)
    course_id = models.CharField(max_length=25, blank=True, null=True)
    prof_last_name = models.CharField(max_length=225, null=True, blank=True)
    prof_first_name = models.CharField(max_length=225, null=True, blank=True)
    class_days = models.ManyToManyField(Days, related_name="class_days")
    start_time = models.TimeField()
    end_time = models.TimeField()
    year = models.IntegerField()
    term = models.CharField(max_length=225)

    class Meta:
        unique_together = (('course_id', 'year', 'term'),)


class Student(User):
    student_id = models.CharField(max_length=30, unique=True)
    courses = models.ManyToManyField(Course)

    def save(self, *args, **kwargs):
        super(Student, self).save(*args, **kwargs)
