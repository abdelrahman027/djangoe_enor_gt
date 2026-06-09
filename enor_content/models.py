from django.db import models

# Create your models here.
class FAQ(models.Model):
    question = models.CharField(max_length=300)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return self.question
    
class Contact_us(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    subject = models.CharField(max_length=1024, blank=True)
    message = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Contact us from {self.email} - {self.subject}" if self.subject else self.name
    def save(self, *args, **kwargs):
        if not self.subject:
            self.subject = f"Contact us from {self.email}"
        super().save(*args, **kwargs)
        
        
class Social_links(models.Model):
    name = models.CharField(max_length=50)
    link = models.URLField(max_length=255)
    icon = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'created_at']
        
    def __str__(self):
        return self.name

class Newsletter(models.Model):
    email = models.EmailField(max_length=255)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        
        return self.email