from django.db import models
from django.contrib.auth.models import User

# School Programs
class Program(models.Model):
    program_name = models.CharField(max_length=120, unique=True)
    tuition = models.IntegerField()

    def __str__(self):
        return ("{}".format(self.program_name).upper())

    def count_objs(self):
        return self.objects.all().count()

# Students Personal info class
class Student(models.Model):
    username = models.OneToOneField(User, on_delete=models.CASCADE)
    tuition = models.IntegerField()
    program = models.ForeignKey(Program, on_delete=models.CASCADE)

    def __str__(self):
        return ("{}".format(self.username).lower())

class Term(models.Model):
    name = models.CharField(max_length=30)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return "{} {}".format(self.name, self.end_date.year).upper()

    def is_valid_term(self):
        return self.start_date < self.end_date

class Payment(models.Model):
    """Student payments Term 1"""
    amount = models.IntegerField()
    pay_date = models.DateField()
    student = models.ForeignKey(Student, related_name='payment', on_delete=models.CASCADE)
    term = models.ForeignKey(Term, related_name="term", on_delete=models.CASCADE)

    def __str__(self):
        return "Amount: {} Student Info: {}".format(self.amount, self.student)
