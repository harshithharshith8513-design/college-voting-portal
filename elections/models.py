from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Election(models.Model):
    ELECTION_STATUS = [
        ('upcoming', 'Upcoming'),
        ('active', 'Active'),
        ('ended', 'Ended'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=ELECTION_STATUS, default='upcoming')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def is_active(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date and self.status == 'active'

    def __str__(self):
        return self.title

class Position(models.Model):
    name = models.CharField(max_length=100)
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    max_candidates = models.IntegerField(default=10)

    def __str__(self):
        return f"{self.name} - {self.election.title}"

class Candidate(models.Model):
    name = models.CharField(max_length=100)
    student_id = models.CharField(max_length=20)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    manifesto = models.TextField()
    photo = models.ImageField(upload_to='candidates/', blank=True)
    vote_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} - {self.position.name}"

class Vote(models.Model):
    voter = models.ForeignKey(User, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['voter', 'position']

    def __str__(self):
        return f"{self.voter.username} voted for {self.candidate.name}"
