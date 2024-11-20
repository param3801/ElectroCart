from django.db import models

STATUS_CHOICE=(
    ('Accepted','Accepted'),
    ('Packed','Packed'),
    ('On the way','On the way'),
    ('Delivered','Delivered'),
    ('Cancel','Cancel'),


)

class OrderDetail(models.Model):
    user= models.CharField(default= True,max_length=15)
    product_name=models.CharField(max_length=250)
    image=models.ImageField(null=True,blank=True)
    qty=models.PositiveIntegerField(default=1)
    price=models.IntegerField()
    order_date=models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=50,default='pending',choices=STATUS_CHOICE)