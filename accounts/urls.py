
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

urlpatterns = [
    # Authentication
    path('accounts/', views.SignUpView.as_view(), name='signup'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),

    # Tutor
    path('tutor/dashboard/', views.tutor_dashboard, name='tutor_dashboard'),
    path('tutor/upload/', views.tutor_upload_book, name='tutor_upload_book'),
    path('tutor/books/', views.tutor_books, name='tutor_books'),
    path('tutor/earnings/', views.tutor_earnings, name='tutor_earnings'),

    # Manager
    path('manager/dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('manager/tutors/', views.tutor_list, name='tutor_list'),
    path('manager/tutors/create/', views.create_tutor, name='create_tutor'),
    path('manager/tutors/<int:user_id>/toggle/', views.toggle_user, name='toggle_user'),

    # Manager viewing an individual tutor's books
    path(
        'manager/tutors/<int:user_id>/books/',
        views.tutor_books,
        name='tutor_books'
    ),

    # Alternative manager tutor-books route, if used elsewhere
    path(
        'manager/tutor/<int:tutor_id>/books/',
        views.manager_tutor_books,
        name='manager_tutor_books'
    ),

    path('manager/pending/', views.pending_tutors, name='pending_tutors'),
    path('manager/approve/<int:user_id>/', views.approve_tutor, name='approve_tutor'),
    path('manager/students/', views.manager_students, name='manager_students'),
    path('manager/books/', views.manager_books, name='manager_books'),
    path('manager/tutors/list/', views.manager_tutors, name='manager_tutors'),

    # Notifications
    path('notifications/read/', views.mark_notifications_read, name='mark_notifications_read'),

    # Admin
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/users/', views.all_users, name='all_users'),
    path('admin-panel/users/toggle/<int:user_id>/', views.admin_toggle_user, name='admin_toggle_user'),
    path('admin-panel/create-manager/', views.create_manager, name='create_manager'),
    path('admin-panel/books/', views.admin_books, name='admin_books'),


    # User Profile
path('profile/', views.user_profile, name='user_profile'),

# Change Password
path(
    'change-password/',
    auth_views.PasswordChangeView.as_view(
        template_name='accounts/change_password.html',
        success_url='/password-changed/'
    ),
    name='change_password'
),

# Password Changed Successfully
path(
    'password-changed/',
    auth_views.PasswordChangeDoneView.as_view(
        template_name='accounts/password_changed.html'
    ),
    name='password_changed'
),

# Password Reset
path(
    'password-reset/',
    auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset.html',
        email_template_name='accounts/password_reset_email.html',
        subject_template_name='accounts/password_reset_subject.txt',
        success_url=reverse_lazy('password_reset_done'),
    ),
    name='password_reset'
),

path(
    'password-reset/done/',
    auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ),
    name='password_reset_done'
),

path(
    'password-reset/<uidb64>/<token>/',
    auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html',
        success_url=reverse_lazy('password_reset_complete'),
    ),
    name='password_reset_confirm'
),

path(
    'password-reset/complete/',
    auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ),
    name='password_reset_complete'
),
    
]
 