from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date


# 👤 CUSTOM USER
class User(AbstractUser):
    ROLE_CHOICES = (
        ('DONOR', 'Donor'),
        ('NGO', 'NGO'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='DONOR')

    # optional fields (safe)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)


# 💊 MEDICINE DONATION
class MedicineDonation(models.Model):

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
    ]

    donor = models.ForeignKey(User, on_delete=models.CASCADE)

    medicine_name = models.CharField(max_length=100)
    quantity = models.IntegerField()

    expiry_date = models.DateField()
    city = models.CharField(max_length=100)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')

    # optional image
    image = models.ImageField(upload_to='medicine_images/', blank=True, null=True)

    def days_left(self):
        return (self.expiry_date - date.today()).days


# 📦 MEDICINE REQUEST (🔥 TRACKING ADDED HERE)
class MedicineRequest(models.Model):

    STATUS_CHOICES = [
        ('REQUESTED', 'Requested'),
        ('APPROVED', 'Approved'),
        ('PACKED', 'Packed'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('REJECTED', 'Rejected'),
    ]

    ngo = models.ForeignKey(User, on_delete=models.CASCADE)
    donation = models.ForeignKey(MedicineDonation, on_delete=models.CASCADE)

    quantity = models.IntegerField(default=1)

    reason = models.TextField(blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='REQUESTED'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ngo.username} - {self.donation.medicine_name} ({self.status})"