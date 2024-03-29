from django.db import models
from billing.models import BillingProfile
from cart.models import Cart
from django.db.models.signals import pre_save,post_save
from mysite.utils import unique_id_generator
from addresses.models import Address
# Create your models here.
ORDER_STATUS_CHOICES=(
    ('created','Created'),
    ('paid','Paid'),
    ('shipped','Shipped'),
    ('refunded','Refunded'),
)

class OrderManager(models.Manager):
    def new_or_get(self,billingProfile,cart_obj):
        qs=self.get_queryset().filter(billingProfile=billingProfile,cart=cart_obj,active=True,status='created')
        if qs.exists():
            order_obj_created=False
            obj=qs.first()
        else:
            obj=self.model.objects.create(billingProfile=billingProfile , cart=cart_obj)
            order_obj_created=True
        return obj,order_obj_created



class Order(models.Model):
    billingProfile=models.ForeignKey(BillingProfile,null=True,blank=True)
    order_id=models.CharField(max_length=120,blank=True)
    shipping_address=models.ForeignKey(Address,related_name='shipping_address',null=True,blank=True)
    billing_address=models.ForeignKey(Address,related_name='billing_address',null=True,blank=True)
    cart=models.ForeignKey(Cart)
    status=models.CharField(max_length=120,default='created',choices=ORDER_STATUS_CHOICES)
    shipping_total=models.DecimalField(default=5.99,max_digits=100,decimal_places=2)
    total=models.DecimalField(default=0.00,max_digits=100,decimal_places=2)
    active=models.BooleanField(default=True)

    objects=OrderManager()

    def __str__(self):
        return self.order_id

    def update_total(self):
        import math
        cart_total=self.cart.total
        shipping_total=self.shipping_total
        new_total=math.fsum([cart_total,shipping_total])
        formatted_total=format(new_total,'.2f')
        self.total=formatted_total
        self.save()
        return new_total

    def check_done(self):
        billing_profile=self.billingProfile
        shipping_address=self.shipping_address
        billing_address=self.billing_address
        total=self.total
        if billing_profile and shipping_address and billing_address and total > 0:
            return True

        return False

    def mark_paid(self):
        if self.check_done():
            self.status='paid'
            self.save()
        return self.status

def pre_save_create_order_id(sender,instance,*agrs,**kwargs):
    if not instance.order_id:
        instance.order_id=unique_id_generator(instance)
    qs=Order.objects.filter(cart=instance.cart).exclude(billingProfile=instance.billingProfile)
    if qs.exists():
        qs.update(active=False)

pre_save.connect(pre_save_create_order_id,sender=Order)

def post_save_cart_total(sender,instance,created,*args,**kwargs):
    if not created:
        cart_obj=instance
        cart_total=cart_obj.total
        cart_id=cart_obj.id
        qs=Order.objects.filter(cart__id=cart_id)
        if qs.count()==1:
            order_obj=qs.first()
            order_obj.update_total()

post_save.connect(post_save_cart_total,sender=Cart)

def post_save_order(sender,instance,created,*args,**kwargs):
    if created:
        instance.update_total()

post_save.connect(post_save_order,sender=Order)
