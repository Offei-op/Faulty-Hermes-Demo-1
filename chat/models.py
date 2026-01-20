from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('fr', 'French'),
        ('es', 'Spanish'),
        # Add more as needed
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    target_language = models.CharField(
        max_length=5, 
        choices=LANGUAGE_CHOICES, 
        default='en'
    )
    friends = models.ManyToManyField("self", blank=True)

    def __str__(self):
        return f"{self.user.username} - Learning {self.get_target_language_display()}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        Profile.objects.get_or_create(user=instance)


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    original_text = models.TextField()
    translated_text = models.TextField() # What the receiver sees
    english_text = models.TextField()    # For the shadow bubble
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']