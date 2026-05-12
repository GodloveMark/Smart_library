from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from .forms import CustomUserCreationForm
from django.contrib.auth.views import LoginView
from books.models import Book


def is_manager(user):
    return user.is_authenticated and user.user_type == 'manager'

def is_admin(user):
    return user.is_authenticated and user.user_type == 'admin'


class SignUpView(generic.CreateView):
    form_class = CustomUserCreationForm
    template_name = 'signup.html'
    success_url = reverse_lazy('login')


class CustomLoginView(LoginView):
    template_name = 'login.html'
    # print ("Tutor")

    def get_success_url(self):
        user = self.request.user
    
        print("USER TYPE:", user.user_type)  
    
        if user.user_type == 'tutor':
            print("Redirecting to tutor dashboard")
            return reverse_lazy('tutor_dashboard')
    
        elif user.user_type == 'manager':
            print("Redirecting to manager dashboard")
            return reverse_lazy('manager_dashboard')
    
        elif user.user_type == 'student':
            print("Redirecting to book list")
            return reverse_lazy('list')

        elif user.user_type == 'admin':
            print("Redirecting to book list")
            return reverse_lazy('admin_dashboard')
    
    
        return reverse_lazy('login')


from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

@login_required
def tutor_dashboard(request):
    if request.user.user_type != 'tutor':
        raise PermissionDenied("Only tutors allowed")

    books = Book.objects.filter(tutor=request.user)

    return render(request, 'tutor/dashboard.html', {'books': books})



from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')




from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

User = get_user_model()


@login_required
def create_tutor(request):
    if request.user.user_type != 'manager':
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("create_tutor")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            user_type='tutor',
            is_active=False
        )

        # ✅ Notify managers (INSIDE POST)
        managers = User.objects.filter(user_type='manager')

        for m in managers:
            Notification.objects.create(
                user=m,
                message=f"New tutor '{username}' is waiting for approval"
            )

        messages.success(request, "Tutor created successfully")
        return redirect("tutor_list")

    # ✅ GET request
    return render(request, "manager/create_tutor.html")

@login_required
def tutor_list(request):
    if request.user.user_type != 'manager':
        return redirect('home')

    tutors = User.objects.filter(user_type='tutor')

    return render(request, "manager/tutor_list.html", {
        "tutors": tutors
    })




@login_required
def toggle_user(request, user_id):
    if request.user.user_type != 'manager':
        return redirect('home')

    user = User.objects.get(id=user_id)
    user.is_active = not user.is_active
    user.save()

    return redirect('tutor_list')


from django.db.models import Sum
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Notification


User = get_user_model()


@login_required
def manager_dashboard(request):
    if request.user.user_type != 'manager':
        return redirect('home')

    total_tutors = User.objects.filter(user_type='tutor').count()
    total_students = User.objects.filter(user_type='student').count()
    total_books = Book.objects.count()

    # simple revenue (sum of book prices)
    total_revenue = Book.objects.aggregate(Sum('price'))['price__sum'] or 0

    latest_books = Book.objects.order_by('-created_at')[:5]
    latest_tutors = User.objects.filter(user_type='tutor').order_by('-date_joined')[:5]

    context = {
        "total_tutors": total_tutors,
        "total_students": total_students,
        "total_books": total_books,
        "total_revenue": total_revenue,
        "latest_books": latest_books,
        "latest_tutors": latest_tutors,
    }

    return render(request, "manager/dashboard.html", context)


@login_required
def tutor_books(request, user_id):
    if request.user.user_type != 'manager':
        return redirect('home')

    tutor = User.objects.get(id=user_id)
    books = Book.objects.filter(tutor=tutor)

    return render(request, "manager/tutor_books.html", {
        "tutor": tutor,
        "books": books
    })



@login_required
def approve_tutor(request, user_id):
    if request.user.user_type != 'manager':
        return redirect('home')

    tutor = User.objects.get(id=user_id)
    tutor.is_active = True
    tutor.save()

    # notify tutor
    Notification.objects.create(
        user=tutor,
        message="Your tutor account has been approved ✅"
    )

    return redirect('tutor_list')

def pending_tutors(request):
    tutors = User.objects.filter(user_type='tutor', is_active=False)
    return render(request, "manager/pending_tutors.html", {"tutors": tutors})


def mark_notifications_read(request):
    request.user.notification_set.update(is_read=True)
    return redirect(request.META.get('HTTP_REFERER'))



from django.db.models import Sum

@login_required
def admin_dashboard(request):
    if request.user.user_type != 'admin':
        return redirect('home')

    total_users = User.objects.count()
    total_tutors = User.objects.filter(user_type='tutor').count()
    total_managers = User.objects.filter(user_type='manager').count()
    total_students = User.objects.filter(user_type='student').count()

    total_books = Book.objects.count()
    total_revenue = Book.objects.aggregate(Sum('price'))['price__sum'] or 0

    context = {
        "total_users": total_users,
        "total_tutors": total_tutors,
        "total_managers": total_managers,
        "total_students": total_students,
        "total_books": total_books,
        "total_revenue": total_revenue,
    }

    return render(request, "admin_panel/dashboard.html", context)

@login_required
def all_users(request):
    if request.user.user_type != 'admin':
        return redirect('home')

    users = User.objects.all().order_by('-date_joined')

    return render(request, "admin_panel/users.html", {"users": users})


@login_required
def admin_toggle_user(request, user_id):
    if request.user.user_type != 'admin':
        return redirect('home')

    user = User.objects.get(id=user_id)
    user.is_active = not user.is_active
    user.save()

    return redirect('all_users')

@login_required
def create_manager(request):
    if request.user.user_type != 'admin':
        return redirect('home')

    if request.method == "POST":
        user = User.objects.create_user(
            username=request.POST['username'],
            email=request.POST['email'],
            password=request.POST['password'],
            user_type='manager'
        )
        return redirect('all_users')

    return render(request, "admin_panel/create_manager.html")


@login_required
def admin_books(request):
    if request.user.user_type != 'admin':
        return redirect('home')

    books = Book.objects.all().order_by('-created_at')

    return render(request, "admin_panel/books.html", {"books": books})





from django.db.models import Count
from django.db.models.functions import TruncDate

def daily_users():
    return UserActivity.objects.annotate(
        day=TruncDate('date')
    ).values('day').annotate(count=Count('id')).order_by('day')
