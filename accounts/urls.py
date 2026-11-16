
from django.urls import path
from . import views

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
    path('manager/tutors/<int:user_id>/books/', views.manager_tutor_books, name='manager_tutor_books'),
    path('manager/pending/', views.pending_tutors, name='pending_tutors'),
    path('manager/approve/<int:user_id>/', views.approve_tutor, name='approve_tutor'),
    path('manager/students/', views.manager_students, name='manager_students'),
    path('manager/books/', views.manager_books, name='manager_books'),
    path('manager/tutors/', views.manager_tutors, name='manager_tutors'),

    # Notifications
    path('notifications/read/', views.mark_notifications_read, name='mark_notifications_read'),

    # Admin
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/users/', views.all_users, name='all_users'),
    path('admin-panel/users/toggle/<int:user_id>/', views.admin_toggle_user, name='admin_toggle_user'),
    path('admin-panel/create-manager/', views.create_manager, name='create_manager'),
    path('admin-panel/books/', views.admin_books, name='admin_books'),
   
]
