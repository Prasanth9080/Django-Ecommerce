from django.db import models
from django.contrib.auth.models import User

# Create your models here.

CATEGORY_CHOICES=(
    ('CR', 'Curd'),
    ('ML', 'Milk'),
    ('LS', 'Lassi'),
    ('MS', 'Milkshake'),
    ('PN', 'Panner'),
    ('GH', 'Ghee'),
    ('CZ', 'Cheese'),
    ('IC', 'Ice-Creams')
)

STATE_CHOICES = (
('Andaman & Nicobar Islands', 'Andaman & Nicobar Islands'),
('Andhra Pradesh', 'Andhra Pradesh'),
('Arunachal Pradesh', 'Arunachal Pradesh'),
('Assam', 'Assam'),
('Bihar', 'Bihar'),
('Chandigarh', 'Chandigarh'),
('Chattisgarh', 'Chattisgarh'),
('Dadra & Nagar Haveli', 'Dadra & Nagar Haveli'),
('Daman and Diu', 'Daman and Diu'),
('Delhi', 'Delhi'),
('Goa', 'Goa'),
('Gujrat', 'Gujrat'),
('Haryana', 'Haryana'),
('Himachal Pradesh', 'Himachal Pradesh'),
('Jammu & Kashmir','Jammu & Kashmir'),
('Jharkhand', 'Jharkhand'),
('Karnataka', 'Karnataka'),
('Kerala', 'Kerala'),
('Lakshadweep', 'Lakshadweep'),
('Madhya Pradesh', 'Madhya Pradesh'),
('Maharashtra', 'Maharashtra'),
('Manipur', 'Manipur'),
('Meghalaya', 'Meghalaya'),
('Mizoram', 'Mizoram'),
('Nagaland', 'Nagaland'),
('Odisa', 'Odisa' ),
('Puducherry', 'Puducherry'),
('Punjab', 'Punjab'),
('Rajasthan', 'Rajasthan'), 
('Sikkim', 'Sikkim'),
('Tamil Nadu', 'Tamil Nadu'),
('Telangana', 'Telangana'),
('Tripura', 'Tripura'),
('Uttarakhand', 'Uttarakhand'),
('Uttar Pradesh', 'Uttar Pradesh'),
('West Bengal', 'West Bengal'),
)

#carousel
class CarouselImage(models.Model):
    image = models.ImageField(upload_to='carousel_images/')
    caption = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.caption or 'No Caption'

class Product(models.Model):
    category = models.CharField(max_length=2, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=100)
    selling_price = models.FloatField()
    discount_price = models.FloatField()
    description = models.TextField()
    composition = models.TextField()
    prodapp = models.CharField(choices=CATEGORY_CHOICES, max_length=2, default="")
    product_image = models.ImageField(upload_to='product')
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)

    def __str__(self):
        return self.title


# models.py
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    locality = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(choices=STATE_CHOICES,max_length=100)
    zipcode = models.CharField(max_length=10)

class Cart(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
 
    @property
    def total_cost(self):
        return self.quantity * self.product.discount_price

STATUS_CHOICES = (
    ('Accepted', 'Accepted'),
    ('Packed', 'Packed'),
    ('On The Way', 'On The Way'),
    ('Delivered', 'Delivered'),
    ('Cancel', 'Cancel'),
    ('Pending', 'Pending'),
)

#payment process
class Payment(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    amount=models.FloatField()
    razorpay_order_id = models.CharField(max_length=100,blank=True,null=True)  
    razorpay_payment_status = models.CharField(max_length=100,blank=True,null=True)
    razorpay_payment_id = models.CharField(max_length=100,blank=True,null=True)
    paid = models.BooleanField(default=False)

#Click Continue button function
class OrderPlaced(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    ordered_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50,choices=STATUS_CHOICES, default="Pending")
    payment = models.ForeignKey(Payment,on_delete=models.CASCADE,default="")
    @property
    def total_cost(self):
        return self.quantity * self.product.discount_price      

