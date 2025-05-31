from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.conf import settings

# Create your models here.

class CustomUser(AbstractUser):
    ROLE_CHOICES = [('student', 'Student'), ('admin', 'Admin')]
    STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    student_id = models.CharField(max_length=255, unique=True, null=True, blank=True)  # Optional for admin users
    first_name = models.CharField(max_length=150, blank=True)  # Explicitly included for clarity
    last_name = models.CharField(max_length=150, blank=True)   # Explicitly included for clarity
    course = models.CharField(max_length=255, null=True, blank=True)
    program = models.CharField(max_length=255, null=True, blank=True)
    year_level = models.PositiveIntegerField(null=True, blank=True)
    partylist = models.ForeignKey('PartyList', on_delete=models.SET_NULL, null=True, blank=True)
    password = models.CharField(max_length=255) 
    remember_token = models.CharField(max_length=255, null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    photo_url = models.ImageField(upload_to='profile_pictures/', default='profile_pictures/default_user_profile2.png')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

# Positions Model
class Position(models.Model):
    PROGRAM_CHOICES = [('BSIT', 'BSIT'), ('BSCS', 'BSCS'), ('BSEMC', 'BSEMC'), ('ALL', 'ALL')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    position_name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    program = models.CharField(max_length=10, choices=PROGRAM_CHOICES, default='ALL')
    rank = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.position_name or "")


# Elections Model
class Election(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.title or "")


# PartyList Model
class PartyList(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    party_leader_name = models.CharField(max_length=255)
    party_name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    vision = models.TextField(null=True, blank=True)
    mission = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_parties')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    is_finalized = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.party_name or "")

class PartyRequest(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    party = models.ForeignKey('PartyList', on_delete=models.CASCADE)
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='requested_parties')
    requested_member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='party_requests')
    position = models.ForeignKey('Position', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{str(self.requester)} -> {str(self.requested_member)} ({self.status})"


class Candidate(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    election = models.ForeignKey('Election', on_delete=models.CASCADE, db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=50)
    position = models.ForeignKey('Position', on_delete=models.CASCADE)
    partylist = models.ForeignKey('PartyList', on_delete=models.SET_NULL, null=True, blank=True)
    platform = models.TextField(null=True, blank=True)
    achievements = models.TextField(null=True, blank=True)
    leadership_experience = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('election', 'student_id', 'position')

    def __str__(self):
        return f"{str(self.user)} - {self.status}"
    
class AuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    details = models.TextField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Action by {str(self.user)} - {self.action}"

class Vote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    election = models.ForeignKey('Election', on_delete=models.CASCADE)
    candidate = models.ForeignKey('Candidate', on_delete=models.CASCADE)
    position = models.ForeignKey('Position', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('election', 'user', 'position')

    def __str__(self):
        # pylint: disable=no-member
        return f"Vote by {str(self.user.email)} for {str(self.candidate.user)}"
        # pylint: enable=no-member
