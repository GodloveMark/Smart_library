
from django.urls import path
from .views import BooksListView,summarize_book_view, delete_book, chat_with_book, upload_book, BooksDetailView, BookCheckoutView, paymentComplete, SearchResultsListView
from . import views

urlpatterns = [
    path('', BooksListView.as_view(), name = 'list'),
    path('<int:pk>/', BooksDetailView.as_view(), name = 'detail'),
    path('<int:pk>/checkout/', BookCheckoutView.as_view(), name = 'checkout'),
    path('complete/', paymentComplete, name = 'complete'),
    path('search/', SearchResultsListView.as_view(), name = 'search_results'),
    path('tutor/upload/', upload_book, name='upload_book'),
    #path('<int:pk>/', book_detail, name='detail'),
    #path('<int:pk>/read/', read_book, name='read_book'),
    #path('<int:pk>/add_note/', add_note, name='add_note'),
    #path('save-highlight/<int:pk>/', save_highlight, name='save_highlight'),
    #path('bookmark-page/<int:pk>/', bookmark_page, name='bookmark_page'),
    #path('save-progress/<int:pk>/', save_progress, name='save_progress'),
    path('<int:pk>/chat/', chat_with_book, name='chat_with_book'),
    path('summarize/<int:pk>/', summarize_book_view, name='summarize_book'),


    path(
        '<int:pk>/read/',
        views.read_book,
        name='read_book'
    ),

    path(
        '<int:pk>/add_note/',
        views.add_note,
        name='add_note'
    ),

    path(
        '<int:pk>/save_highlight/',
        views.save_highlight,
        name='save_highlight'
    ),

    path(
        '<int:pk>/bookmark/',
        views.bookmark_page,
        name='bookmark_page'
    ),

    path(
        '<int:pk>/save_progress/',
        views.save_progress,
        name='save_progress'
    ),

    path(
        '<int:pk>/save_annotation/',
        views.save_annotation,
        name='save_annotation'
    ),


    path(
        '<int:pk>/delete-study-item/<str:item_type>/<int:item_id>/',
        views.delete_study_item,
        name='delete_study_item'
    ),


    path(
        'tutor/books/<int:pk>/delete/',
        delete_book,
        name='delete_book'
    ),

    
]
