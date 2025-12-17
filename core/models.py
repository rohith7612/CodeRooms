from django.db import models
from django.contrib.auth.models import User
import uuid
import random
import string

class Problem(models.Model):
    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    topic = models.CharField(max_length=50)  # e.g., "Arrays", "DP"
    initial_code = models.TextField(help_text="Starting code template")
    test_cases = models.JSONField(help_text="List of input/output pairs", default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

def generate_room_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

class Room(models.Model):
    room_id = models.CharField(max_length=6, unique=True, default=generate_room_id)
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_rooms')
    passcode = models.CharField(max_length=20, blank=True, null=True)
    problem = models.ForeignKey(Problem, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Configuration (snapshot of what was asked even if problem isn't selected yet)
    topic = models.CharField(max_length=50, blank=True)
    difficulty = models.CharField(max_length=10, blank=True)
    anti_cheat_enabled = models.BooleanField(default=False, help_text="Enable tab-switching detection")

    def __str__(self):
        return f"Room {self.room_id}"

class Participant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='participants')
    score = models.IntegerField(default=0)
    completed_test_cases = models.IntegerField(default=0)
    tab_switches = models.IntegerField(default=0)
    joined_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('user', 'room')

    def __str__(self):
        return f"{self.user.username} in {self.room.room_id}"

class Submission(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='submissions')
    code = models.TextField()
    passed = models.BooleanField(default=False)
    output_log = models.TextField(blank=True)
    execution_time = models.FloatField(default=0.0, help_text="Execution time in seconds")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Submission by {self.participant.user.username} - {'Pass' if self.passed else 'Fail'}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    rating = models.IntegerField(default=1200) # Standard ELO starting point
    matches_played = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username} - {self.rating}"

# Signal to create/update profile
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
