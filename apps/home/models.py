# models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
import os

class Color(models.Model):
    color = models.CharField(max_length=10, default="#ba54f5")
    gradient = models.BooleanField(default=True)
    gradient_color = models.CharField(max_length=10, default="#e14eca")

# 個人資料
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    real_name = models.CharField(max_length=100, blank=True, null=True)
    contact_address = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Save old photo instance for deletion later
        if self.pk:
            try:
                old_instance = Profile.objects.get(pk=self.pk)
                if old_instance.photo and old_instance.photo != self.photo:
                    old_instance.photo.delete(save=False)
            except Profile.DoesNotExist:
                pass

def get_cover_image_filename(instance, filename):
    dir_path = os.path.join("product_images", instance.product_name)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return os.path.join(dir_path, "cover" + os.path.splitext(filename)[1])

def get_additional_image_filename(instance, filename):
    dir_path = os.path.join("product_images", instance.product.product_name)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    existing_files = [f for f in os.listdir(dir_path) if f.startswith("image")]
    index = len(existing_files)
    return os.path.join(dir_path, f"image{index}" + os.path.splitext(filename)[1])

# 商品資料
class Product(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    product_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    address = models.CharField(max_length=255)
    description = models.TextField()
    price = models.IntegerField()
    image = models.ImageField(upload_to=get_cover_image_filename)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Save old image instance for deletion later
        if self.pk:
            try:
                old_instance = Product.objects.get(pk=self.pk)
                if old_instance.image and old_instance.image != self.image:
                    old_instance.image.delete(save=False)
            except Product.DoesNotExist:
                pass

# 商品照片
class ProductImage(models.Model):
    product = models.ForeignKey(Product, default=None, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=get_additional_image_filename, verbose_name='Image')

# 感測器
class Sensor(models.Model):
    name = models.CharField(max_length=100)

# 感測器數據
class SensorData(models.Model):
    name = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    data = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

# Signals for deleting files when a model instance is deleted
@receiver(post_delete, sender=Profile)
def delete_profile_photo(sender, instance, **kwargs):
    if instance.photo:
        instance.photo.delete(save=False)

@receiver(post_delete, sender=Product)
def delete_product_image(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete(save=False)

@receiver(post_delete, sender=ProductImage)
def delete_product_image_file(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete(save=False)

# Signals for deleting old files when a new file is saved
@receiver(pre_save, sender=Profile)
def delete_old_profile_photo(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = Profile.objects.get(pk=instance.pk)
            if old_instance.photo and old_instance.photo != instance.photo:
                old_instance.photo.delete(save=False)
        except Profile.DoesNotExist:
            pass

@receiver(pre_save, sender=Product)
def delete_old_product_image(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = Product.objects.get(pk=instance.pk)
            if old_instance.image and old_instance.image != instance.image:
                old_instance.image.delete(save=False)
        except Product.DoesNotExist:
            pass
