from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.


class VideoSummary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video_url = models.URLField()
    video_title = models.CharField(max_length=200)
    summary = models.TextField()
    short_description = models.TextField(default="No short description available.")
    thumbnail_url = models.URLField(blank=True, null=True)  # New field for thumbnail
    key_points = models.JSONField(default=list)  # New field for key points
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.video_title} - {self.user.username}"

    class Meta:
        ordering = ["-created_at"]


class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    video_summaries = models.ManyToManyField(VideoSummary)  # Link to VideoSummary

    def __str__(self):
        return f"{self.user.username} - {self.query}"

    class Meta:
        verbose_name_plural = "Search histories"
        ordering = ["-created_at"]


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    preferred_language = models.CharField(max_length=50, default="English")
    summary_length = models.CharField(
        max_length=20,
        choices=[("short", "Short"), ("medium", "Medium"), ("long", "Long")],
        default="medium",
    )

    def __str__(self):
        return self.user.username


class ScrapedVideo(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    url = models.URLField()
    title = models.CharField(max_length=255)
    thumbnail = models.URLField()
    scraped_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()
