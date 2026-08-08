
from django.urls import path
from .views import SignUpView,approve_tutor,mark_notifications_read,admin_dashboard,all_users,admin_toggle_user,create_manager,admin_books, CustomLoginView, tutor_dashboard, CustomLogoutView,tutor_list, create_tutor, manager_dashboard, toggle_user, tutor_books, pending_tutors
from . import views


urlpatterns = [
    path('accounts/', SignUpView.as_view(), name = 'signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('tutor/dashboard/', tutor_dashboard, name='tutor_dashboard'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('manager/tutors/', tutor_list, name='tutor_list'),
    path('manager/tutors/create/', create_tutor, name='create_tutor'),
    path('manager/dashboard/', manager_dashboard, name='manager_dashboard'),
    path('manager/tutors/<int:user_id>/toggle/', toggle_user, name='toggle_user'),
    path('manager/tutors/<int:user_id>/books/', tutor_books, name='tutor_books'),
    path('manager/pending/', pending_tutors, name='pending_tutors'),
path('manager/approve/<int:user_id>/', approve_tutor, name='approve_tutor'),
path('notifications/read/', mark_notifications_read, name='mark_notifications_read'),
path('admin-panel/', admin_dashboard, name='admin_dashboard'),
path('admin-panel/users/', all_users, name='all_users'),
path('admin-panel/users/toggle/<int:user_id>/', admin_toggle_user, name='admin_toggle_user'),
path('admin-panel/create-manager/', create_manager, name='create_manager'),
path('admin-panel/books/', admin_books, name='admin_books'),

  path(
        'manager/students/',
        views.manager_students,
        name='manager_students'
    ),

    path(
        'manager/tutors/',
        views.manager_tutors,
        name='manager_tutors'
    ),

    path(
        'manager/tutors/<int:tutor_id>/books/',
        views.tutor_books,
        name='tutor_books'
    ),

    path(
        'manager/books/',
        views.manager_books,
        name='manager_books'
    ),

]