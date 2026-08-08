
from django.urls import path
from .views import BooksListView,summarize_book_view, read_book, chat_with_book, save_progress, bookmark_page, save_highlight, add_note, upload_book, BooksDetailView, BookCheckoutView, paymentComplete, SearchResultsListView


urlpatterns = [
    path('', BooksListView.as_view(), name = 'list'),
    path('<int:pk>/', BooksDetailView.as_view(), name = 'detail'),
    path('<int:pk>/checkout/', BookCheckoutView.as_view(), name = 'checkout'),
    path('complete/', paymentComplete, name = 'complete'),
    path('search/', SearchResultsListView.as_view(), name = 'search_results'),
    path('tutor/upload/', upload_book, name='upload_book'),
    #path('<int:pk>/', book_detail, name='detail'),
    path('<int:pk>/read/', read_book, name='read_book'),
    path('<int:pk>/add_note/', add_note, name='add_note'),
    path('save-highlight/<int:pk>/', save_highlight, name='save_highlight'),
    path('bookmark-page/<int:pk>/', bookmark_page, name='bookmark_page'),
    path('save-progress/<int:pk>/', save_progress, name='save_progress'),
    path('<int:pk>/chat/', chat_with_book, name='chat_with_book'),
    path('summarize/<int:pk>/', summarize_book_view, name='summarize_book'),


    
]