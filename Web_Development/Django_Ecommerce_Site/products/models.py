from django.db import models
from django.db.models import Q
from mysite.utils import unique_slug_generator
from django.shortcuts import reverse
from django.db.models.signals import pre_save,post_save
# Create your models here.
class ProductQuerySet(models.query.QuerySet):

    def active(self):
        return self.filter(active=True)

    def featured(self):
        return self.filter(featured=True,active=True)

    def searched(self,query):
        lookups=Q(title__icontains=query)|Q(description__icontains=query)|Q(tag__title__icontains=query)
        return Product.objects.filter(lookups).distinct()

class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model,using=self._db)
    
    def all(self):
        return self.get_queryset().active()

    def features(self):
        return self.get_queryset().featured()

    def get_by_id(self,id):
        qs=self.get_queryset().filter(id=id)
        if qs.count()==1:
            return qs.first()
        return None

    def searches(self,query):
        return self.get_queryset().active().searched(query)

class Product(models.Model):
    title=models.CharField(max_length=120)
    slug=models.SlugField(blank=True,unique=True)
    image=models.ImageField(upload_to='products',null=True,blank=True)
    description=models.TextField()
    price=models.DecimalField(decimal_places=2,max_digits=20,default=20.99)
    featured=models.BooleanField(default=False)
    active=models.BooleanField(default=True)

    objects=ProductManager()

    def get_absolute_url(self):
        return reverse('products:detail', kwargs={'slug':self.slug})
    def __str__(self):
        return self.title

def product_pre_save_receiver(sender,instance,*args,**kwargs):
    if not instance.slug:
        instance.slug=unique_slug_generator(instance)

pre_save.connect(product_pre_save_receiver,sender=Product)