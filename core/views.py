from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date

from .models import User, MedicineDonation, MedicineRequest


# 🏠 HOME
def home(request):
    return render(request, 'home.html')


# 📝 REGISTER
def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        role = request.POST['role']
        phone = request.POST.get('phone', '')  # safe

        User.objects.create_user(
            username=username,
            password=password,
            role=role,
            phone=phone
        )

        return redirect('login')

    return render(request, 'register.html')

# 🔐 LOGIN
def login_view(request): 
    if request.method=='POST':
        username=request.POST.get("username")
        password=request.POST.get("password")
        user=authenticate(request,username=username,password=password)

        if user:
            login(request,user)

            if user.is_superuser:
                return redirect('admin_dashboard')
            elif user.role=='NGO':   
                return redirect('ngo_dashboard')
            else:
                return redirect('dashboard')
        return render(request,'login.html',{'error':'Invalid Credential'})

    return render(request,'login.html')

# 🚪 LOGOUT
def logout_view(request):
    logout(request)
    return redirect('login')


# 📊 DONOR DASHBOARD
@login_required
def dashboard(request):
    donations = MedicineDonation.objects.filter(donor=request.user)

    return render(request, 'dashboard.html', {
        'donations': donations
    })


# ➕ ADD DONATION
@login_required
def add_donation(request):
    if request.method == 'POST':

        image = request.FILES.get('image')  # ✅ important

        MedicineDonation.objects.create(
            donor=request.user,
            medicine_name=request.POST['medicine_name'],
            quantity=request.POST['quantity'],
            expiry_date=request.POST['expiry_date'],
            city=request.POST['city'],
            status='PENDING',
            image=image   # ✅ SAVE IMAGE
        )

        return redirect('dashboard')

    return render(request, 'add_donation.html')


# 🏥 NGO DASHBOARD
@login_required
def ngo_dashboard(request):
    if request.user.role != 'NGO':
        return redirect('dashboard')

    donations = MedicineDonation.objects.filter(status='APPROVED')

    # ✅ ADD DAYS LEFT + USER REQUEST
    for d in donations:
        if d.expiry_date:
            d.days_left = (d.expiry_date - date.today()).days
        else:
            d.days_left = 0

        # 🔥 IMPORTANT (for TRACK button)
        d.user_request = MedicineRequest.objects.filter(
            ngo=request.user,
            donation=d
        ).first()

    expiring_count = sum(1 for d in donations if 0 < d.days_left <= 7)
    city_count = len(set(d.city for d in donations))

    return render(request, 'ngo_dashboard.html', {
        'donations': donations,
        'expiring_count': expiring_count,
        'city_count': city_count
    })


# 📦 REQUEST MEDICINE
@login_required
def request_medicine(request, id):
    donation = get_object_or_404(MedicineDonation, id=id)

    # Check if medicine is expired
    if donation.expiry_date < date.today():
        messages.error(request, "Expired medicine.")
        return redirect('ngo_dashboard')

    if request.method == "POST":
        try:
            req_qty = int(request.POST.get("quantity"))
        except (TypeError, ValueError):
            messages.error(request, "Enter a valid quantity.")
            return redirect('ngo_dashboard')
        # Validation
        if req_qty <= 0:
            messages.error(request, "Quantity must be greater than 0.")
            return redirect('ngo_dashboard')
        if req_qty > donation.quantity:
            messages.error(
                request,
                f"Only {donation.quantity} medicines are available."
            )
            return redirect('ngo_dashboard')
        # Create request
        MedicineRequest.objects.create(
            ngo=request.user,
            donation=donation,
            quantity=req_qty,      # Requires quantity field in model
            reason=request.POST.get('reason', ''),
            status="REQUESTED"
        )
        # Deduct stock
        donation.quantity -= req_qty
        donation.save()

        messages.success(request, "Medicine requested successfully.")
        return redirect('ngo_dashboard')

    return render(request, 'request_form.html', {'donation': donation})
# ⚙️ ADMIN DASHBOARD
@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('dashboard')

    donations = MedicineDonation.objects.all()
    requests = MedicineRequest.objects.all()

    return render(request, 'admin_dashboard.html', {
        'donations': donations,
        'requests': requests,
        'pending_requests': requests.filter(status="REQUESTED").count(),
        'approved_requests': requests.filter(status="APPROVED").count(),
    })


# ✅ APPROVE REQUEST
@login_required
def approve_request(request, id):
    if not request.user.is_superuser:
        return redirect('dashboard')

    req = get_object_or_404(MedicineRequest, id=id)

    if req.donation.expiry_date < date.today():
        req.status = 'REJECTED'
    else:
        req.status = 'APPROVED'

    req.save()
    return redirect('admin_dashboard')


# ❌ REJECT REQUEST
@login_required
def reject_request(request, id):
    if not request.user.is_superuser:
        return redirect('dashboard')

    req = get_object_or_404(MedicineRequest, id=id)
    req.status = 'REJECTED'
    req.save()

    return redirect('admin_dashboard')


# 🚚 TRACK REQUEST (NEW FEATURE)
@login_required
def track_request(request, id):
    req = get_object_or_404(MedicineRequest, id=id)

    return render(request, 'track.html', {
        'req': req
    })
# 📦 MARK AS PACKED
@login_required
def mark_packed(request, id):
    if not request.user.is_superuser:
        return redirect('dashboard')

    req = get_object_or_404(MedicineRequest, id=id)
    req.status = 'PACKED'
    req.save()

    return redirect('admin_dashboard')


# 🚚 MARK AS OUT FOR DELIVERY
@login_required
def mark_out_for_delivery(request, id):
    if not request.user.is_superuser:
        return redirect('dashboard')

    req = get_object_or_404(MedicineRequest, id=id)
    req.status = 'OUT_FOR_DELIVERY'
    req.save()

    return redirect('admin_dashboard')


# 📬 MARK AS DELIVERED
@login_required
def mark_delivered(request, id):
    if not request.user.is_superuser:
        return redirect('dashboard')

    req = get_object_or_404(MedicineRequest, id=id)
    req.status = 'DELIVERED'
    req.save()

    return redirect('admin_dashboard')    


# ✅ APPROVE DONATION
@login_required
def approve_donation(request, id):
    if not request.user.is_superuser:
        return redirect('dashboard')
    
    donation = get_object_or_404(MedicineDonation, id=id)
    donation.status = 'APPROVED'
    donation.save()
    return redirect('admin_dashboard')

# ❌ REJECT DONATION
@login_required
def reject_donation(request, id):
    if not request.user.is_superuser:
        return redirect('dashboard')
    
    donation = get_object_or_404(MedicineDonation, id=id)
    donation.status = 'REJECTED'
    donation.save()
    return redirect('admin_dashboard')    