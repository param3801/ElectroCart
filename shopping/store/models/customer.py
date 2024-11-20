from django.db import models

class Customer(models.Model):
    username = models.CharField(max_length=50)
    phone  = models.CharField(max_length=15)


    def registers(self):
        self.save()


    def isexist(self):
        if Customer.objects.filter(phone=self.phone):
            return True
        else:
            return False     