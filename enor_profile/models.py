from django.db import models
from django.contrib.auth.models import User
from django.templatetags.static import static
# Create your models here.
class UserProfile(models.Model):
    user_roles = [
        ('Customer', 'Customer'),
        ('Editor', 'Editor'),
        ('Admin', 'Admin'),
    ]
    status_choices = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Banned', 'Banned'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='profile')
    image=models.ImageField(upload_to='photos/profile_images', blank=True, null=True)
    real_name = models.CharField(max_length=100, blank=True)
    email=models.EmailField(unique=True,null=True)
    main_phone=models.CharField(max_length=15, blank=True,null=True)
    secondary_phone=models.CharField(max_length=15, blank=True,null=True)
    role=models.CharField(max_length=50,choices=user_roles,default='Customer')
    status=models.CharField(max_length=50,default='Inactive',choices=status_choices)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
    
    @property
    def avatar(self):
        try:
            avatar = self.image.url
        except:
            avatar = static("images/default_avatar.jpg")
        return avatar
    @property
    def name(self):
        if self.real_name:
            name = self.real_name
        else:
            name = self.user.username
        return name
    
    
class UserAddress(models.Model):
    city_choices = [
        ('CAI', 'Cairo'),
        ('ALX', 'Alexandria'),
        ('GZ', 'Giza'),
        ('SHR', 'Sharqia'),
        ('KB', 'Qalyubia'),
        ('MNF', 'Minya'),
        ('WAD', 'New Valley'),
        ('SIN', 'North Sinai'),
        ('SHG', 'South Sinai'),
        ('BNS', 'Beni Suef'),
        ('FSH', 'Faiyum'),
        ('GH', 'Gharbia'),
        ('IS', 'Ismailia'),
        ('KFS', 'Kafr El Sheikh'),
        ('LX', 'Luxor'),
        ('MT', 'Matrouh'),
        ('MN', 'Monufia'),
        ('PTS', 'Port Said'),
        ('SUZ', 'Suez'),
        ('SHW', 'Sohag'),
        ('ASW', 'Aswan'),
        ('AST', 'Asyut'),
        ('DBY', 'Damietta'),
        ('BHR', 'Beheira'),
        ('DGH', 'Dakahlia'),
        ('RED', 'Red Sea'),
        ('QEN', 'Qena'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    address_line1 = models.CharField(max_length=255)
    building_number = models.CharField(max_length=50, blank=True)
    floor=models.CharField(max_length=50, blank=True)
    apartment_number=models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=100, choices=city_choices, default='Cairo')
    address_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.address_line1}, {self.city}"