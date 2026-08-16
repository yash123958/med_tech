from django.contrib import admin
from .models import User, MedicineDonation, MedicineRequest

admin.site.register(User)
admin.site.register(MedicineDonation)
admin.site.register(MedicineRequest)
