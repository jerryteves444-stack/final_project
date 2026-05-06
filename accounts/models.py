from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# ==========================================
# 👤 ADMIN PROFILE MODEL
# ==========================================
class AdminProfile(models.Model):
    ROLE_CHOICES = (
        ('superadmin', 'Super Admin'),
        ('staff', 'Staff Admin'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


# ==========================================
# 👤 USER PROFILE MODEL
# ==========================================
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    profile_picture = models.ImageField(default='defaults.jpg', upload_to='profile_pics')
    cover_photo = models.ImageField(default='cover_defaults.jpg', upload_to='cover_pics')

    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)

    TYPE_CHOICES = [
        ('Sunlight', 'Sunlight'),
        ('Starlight', 'Starlight'),
        ('Alpha', 'Alpha'),
        ('Omega', 'Omega'),
    ]
    user_type = models.CharField(max_length=20, choices=TYPE_CHOICES, blank=True, null=True)

    address = models.TextField(blank=True, null=True)

    # GIDUGANG NGA DATE OF BIRTH FIELD
    dob = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.user.username


# ==========================================
# 📝 POST & COMMENT MODELS
# ==========================================
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


# ==========================================
# ⚡ SIGNALS (AUTOMATIC PROFILE CREATION)
# ==========================================
@receiver(post_save, sender=User)
def manage_user_profile(sender, instance, created, **kwargs):
    """
    Kini nga signal maoy mo-create og Profile o AdminProfile
    depende kung superuser ba ang bag-ong register.
    """
    if created:
        if instance.is_superuser:
            AdminProfile.objects.get_or_create(user=instance, role='superadmin')
        else:
            Profile.objects.get_or_create(user=instance)
    else:
        # I-save ang profile inig update sa User
        if not instance.is_superuser and hasattr(instance, 'profile'):
            instance.profile.save()
        elif instance.is_superuser and hasattr(instance, 'adminprofile'):
            instance.adminprofile.save()

