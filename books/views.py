from django.shortcuts import render 
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin 
from .models import Book, Order
from django.urls import reverse_lazy
from django.db.models import Q # for search method
from django.http import JsonResponse
import json
from accounts.views import tutor_dashboard



class BooksListView(ListView):
    model = Book
    template_name = 'list.html'


class BooksDetailView(DetailView):
    model = Book
    template_name = 'detail.html'


class SearchResultsListView(ListView):
	model = Book
	template_name = 'search_results.html'

	def get_queryset(self): # new
		query = self.request.GET.get('q')
		return Book.objects.filter(
		Q(title__icontains=query) | Q(author__icontains=query)
		)

class BookCheckoutView(LoginRequiredMixin, DetailView):
    model = Book
    template_name = 'checkout.html'
    login_url     = 'login'


def paymentComplete(request):
	body = json.loads(request.body)
	print('BODY:', body)
	product = Book.objects.get(id=body['productId'])
	Order.objects.create(
		product=product
	)
	return JsonResponse('Payment completed!', safe=False)



from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .forms import BookUploadForm
from django.shortcuts import redirect

@login_required
def upload_book(request):
    if request.user.user_type != 'tutor':
        raise PermissionDenied("Only tutors allowed")

    if request.method == 'POST':
        form = BookUploadForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.tutor = request.user  # ✅ assign tutor
            book.save()
            return redirect('tutor_dashboard')
    else:
        form = BookUploadForm()

    return render(request, 'tutor/upload_book.html', {'form': form})



from django.shortcuts import get_object_or_404, render
from .models import Book

from books.models import BookNote
from django.contrib.auth.decorators import login_required

#@login_required
#def read_book(request, pk):
#    book = get_object_or_404(Book, pk=pk)
#    
#    # Fetch existing notes and highlights to display in the sidebar
#    notes = BookNote.objects.filter(user=request.user, book=book).order_by('-created_at')
#    highlights = Highlight.objects.filter(user=request.user, book=book).order_by('-created_at')
#    
#    # Retrieve last progress
#    progress = ReadingProgress.objects.filter(user=request.user, book=book).first()
#    start_page = progress.last_page if progress else 1
#
#    context = {
#        'book': book,
#        'notes': notes,
#        'highlights': highlights,
#        'start_page': start_page,
#    }
#    return render(request, 'books/read.html', context)

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import BookNote, Book
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import Book, BookNote, Highlight, Bookmark, ReadingProgress, BookAnnotation

#@login_required
#@csrf_exempt
#def add_note(request, pk):
#    if request.method == 'POST':
#        data = json.loads(request.body)
#        book = get_object_or_404(Book, pk=pk)
#        note = BookNote.objects.create(
#            user=request.user, 
#            book=book, 
#            note=data.get('note', '').strip(),
#            page=data.get('page', 1)
#        )
#        return JsonResponse({'note': note.note, 'page': note.page})
#
#
#@csrf_exempt
#@login_required
#def save_highlight(request, pk):
#    data = json.loads(request.body)
#    text = data.get('text')
#    page = data.get('page')
#
#    book = get_object_or_404(Book, pk=pk)
#
#    Highlight.objects.create(
#        user=request.user,
#        book=book,
#        text=text,
#        page=page
#    )
#
#    return JsonResponse({'status': 'saved'})
#
#
#from .models import Book, Bookmark  
#
#@login_required
#def bookmark_page(request, pk):
#    if request.method == "POST":
#        data = json.loads(request.body)
#        page = data.get("page")
#
#        book = get_object_or_404(Book, pk=pk)
#
#        Bookmark.objects.create(
#            user=request.user,
#            book=book,
#            page=page
#        )
#
#        return JsonResponse({"status": "saved"})
#
#    return JsonResponse({"error": "Invalid request"}, status=400)
#
#
#
#
#
#
#from .models import Book, ReadingProgress
#
#
#@login_required
#def save_progress(request, pk):
#    if request.method == "POST":
#        data = json.loads(request.body)
#        page = data.get("page")
#        book = get_object_or_404(Book, pk=pk)
#
#        # Atomic update or create
#        ReadingProgress.objects.update_or_create(
#            user=request.user, book=book,
#            defaults={'last_page': page}
#        )
#        return JsonResponse({"status": "saved", "page": page})
#    return JsonResponse({"error": "Invalid request"}, status=400)




def get_json_data(request):
    """Safely read JSON request data."""
    try:
        data = json.loads(request.body or b'{}')
        if not isinstance(data, dict):
            return None
        return data
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


def valid_page(value):
    """Validate PDF page number."""
    try:
        page = int(value)
        return page if page >= 1 else None
    except (TypeError, ValueError):
        return None

from django.views.decorators.http import require_POST



@login_required
@require_POST
def delete_study_item(request, pk, item_type, item_id):
    book = get_object_or_404(Book, pk=pk)

    # Only allow deletion of the current user's records
    models_map = {
        'note': BookNote,
        'highlight': Highlight,
        'bookmark': Bookmark,
        'drawing': BookAnnotation,
        'progress': ReadingProgress,
        'history': ReadingProgress,
    }

    model = models_map.get(item_type)

    if model is None:
        return JsonResponse({
            'success': False,
            'error': 'Invalid item type.'
        }, status=400)

    try:
        with transaction.atomic():
            item = get_object_or_404(
                model,
                pk=item_id,
                book=book,
                user=request.user
            )

            item.delete()

        return JsonResponse({
            'success': True,
            'message': f'{item_type.capitalize()} deleted successfully.',
            'item_type': item_type,
            'item_id': item_id,
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)



import json

@login_required
def read_book(request, pk):
    book = get_object_or_404(Book, pk=pk)

    notes = BookNote.objects.filter(
        user=request.user,
        book=book
    ).order_by('-created_at')

    highlights = Highlight.objects.filter(
        user=request.user,
        book=book
    ).order_by('-created_at')

    bookmarks = Bookmark.objects.filter(
        user=request.user,
        book=book
    ).order_by('page')

    annotations = BookAnnotation.objects.filter(
        user=request.user,
        book=book
    ).order_by('created_at')

    progress = ReadingProgress.objects.filter(
        user=request.user,
        book=book
    ).first()

    start_page = progress.last_page if progress else 1

    context = {
        'book': book,
        'notes': notes,
        'highlights': highlights,
        'bookmarks': bookmarks,
        'annotations': annotations,
        'start_page': start_page,

        'highlights_json': json.dumps([
            {
                'id': h.id,
                'page': h.page,
                'text': h.text,
                'color': h.color,
                'position_data': h.position_data or {}
            }
            for h in highlights
        ]),

        'annotations_json': json.dumps([
            {
                'id': a.id,
                'page': a.page,
                'color': a.color,
                'annotation_type': a.annotation_type,
                'position_data': a.position_data or {}
            }
            for a in annotations
        ]),
    }

    return render(request, 'books/read.html', context)



@login_required
def add_note(request, pk):
    if request.method != 'POST':
        return JsonResponse(
            {'error': 'Invalid request method'},
            status=405
        )

    data = get_json_data(request)

    if data is None:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    note_text = data.get('note', '').strip()
    page = valid_page(data.get('page', 1))

    if not note_text:
        return JsonResponse(
            {'error': 'Note cannot be empty'},
            status=400
        )

    if page is None:
        return JsonResponse(
            {'error': 'Invalid page number'},
            status=400
        )

    book = get_object_or_404(Book, pk=pk)

    note = BookNote.objects.create(
        user=request.user,
        book=book,
        note=note_text,
        page=page
    )

    return JsonResponse({
        'status': 'saved',
        'id': note.id,
        'note': note.note,
        'page': note.page,
        'created_at': note.created_at.isoformat(),
    })


@login_required
def save_highlight(request, pk):
    if request.method != 'POST':
        return JsonResponse(
            {'error': 'Invalid request method'},
            status=405
        )

    data = get_json_data(request)

    if data is None:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    text = data.get('text', '').strip()
    page = valid_page(data.get('page'))
    color = data.get('color', '#FFE66D')
    position_data = data.get('position_data', {})

    if not text or page is None:
        return JsonResponse(
            {'error': 'Highlight text and valid page are required'},
            status=400
        )

    if not isinstance(position_data, dict):
        return JsonResponse(
            {'error': 'Invalid highlight position data'},
            status=400
        )

    book = get_object_or_404(Book, pk=pk)

    highlight = Highlight.objects.create(
        user=request.user,
        book=book,
        text=text,
        page=page,
        color=color,
        position_data=position_data
    )

    return JsonResponse({
        'status': 'saved',
        'id': highlight.id,
        'text': highlight.text,
        'page': highlight.page,
        'color': highlight.color,
    })


@login_required
def bookmark_page(request, pk):
    if request.method != 'POST':
        return JsonResponse(
            {'error': 'Invalid request method'},
            status=405
        )

    data = get_json_data(request)

    if data is None:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    page = valid_page(data.get('page'))

    if page is None:
        return JsonResponse(
            {'error': 'Invalid page number'},
            status=400
        )

    book = get_object_or_404(Book, pk=pk)

    bookmark, created = Bookmark.objects.get_or_create(
        user=request.user,
        book=book,
        page=page
    )

    return JsonResponse({
        'status': 'saved' if created else 'already_saved',
        'id': bookmark.id,
        'page': bookmark.page,
    })


@login_required
def save_progress(request, pk):
    if request.method != 'POST':
        return JsonResponse(
            {'error': 'Invalid request method'},
            status=405
        )

    data = get_json_data(request)

    if data is None:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    page = valid_page(data.get('page'))

    if page is None:
        return JsonResponse(
            {'error': 'Invalid page number'},
            status=400
        )

    book = get_object_or_404(Book, pk=pk)

    progress, created = ReadingProgress.objects.update_or_create(
        user=request.user,
        book=book,
        defaults={'last_page': page}
    )

    return JsonResponse({
        'status': 'saved',
        'page': progress.last_page,
    })


@login_required
def save_annotation(request, pk):
    """Save pencil drawings, underlines and shapes."""

    if request.method != 'POST':
        return JsonResponse(
            {'error': 'Invalid request method'},
            status=405
        )

    data = get_json_data(request)

    if data is None:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    page = valid_page(data.get('page'))
    annotation_type = data.get('annotation_type')
    color = data.get('color', '#FF0000')
    position_data = data.get('position_data', {})

    allowed_types = dict(BookAnnotation.ANNOTATION_TYPES)

    if page is None:
        return JsonResponse(
            {'error': 'Invalid page number'},
            status=400
        )

    if annotation_type not in allowed_types:
        return JsonResponse(
            {'error': 'Invalid annotation type'},
            status=400
        )

    if not isinstance(position_data, dict) or not position_data:
        return JsonResponse(
            {'error': 'Annotation drawing data is required'},
            status=400
        )

    book = get_object_or_404(Book, pk=pk)

    annotation = BookAnnotation.objects.create(
        user=request.user,
        book=book,
        page=page,
        annotation_type=annotation_type,
        color=color,
        position_data=position_data
    )

    return JsonResponse({
        'status': 'saved',
        'id': annotation.id,
        'page': annotation.page,
        'annotation_type': annotation.annotation_type,
    })




import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Book
# Import your utility function from the previous step
from .ai_utils import get_ai_response 

#def chat_with_book(request, pk):
#    if request.method == "POST":
#        try:
#            book = get_object_or_404(Book, pk=pk)
#            data = json.loads(request.body)
#            user_message = data.get("message")
#            
#            # This calls the AI logic
#            answer = get_ai_response(user_message, book.id, book.file.path)
#            
#            return JsonResponse({"answer": answer})
#        except Exception as e:
#            # This helps you see the REAL error in your terminal
#            print(f"AI Error: {e}")
#            return JsonResponse({"answer": "I'm having trouble reading this book right now."}, status=500)
#    return JsonResponse({"status": "Invalid request"}, status=400)


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import json
import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Book
from .ai_utils import get_ai_response


def chat_with_book(request, pk):
    if request.method == "POST":
        try:
            book = get_object_or_404(Book, pk=pk)
            data = json.loads(request.body)

            user_message = data.get("message", "").strip()

            if not user_message:
                return JsonResponse({"answer": "Please ask a question."})

            answer = get_ai_response(
                user_message,
                book.id,
                book.file.path
            )

            return JsonResponse({"answer": answer})

        except Exception as e:
            print(f"AI Error: {e}")
            return JsonResponse(
                {"answer": "AI failed to respond."},
                status=500
            )

    return JsonResponse({"status": "Invalid request"}, status=400)

from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from .models import Book
from .ai_utils import summarize_book   # ✅ THIS LINE


def summarize_book_view(request, pk):
    book = get_object_or_404(Book, pk=pk)

    summary = summarize_book(book.id, book.file.path)

    return JsonResponse({"summary": summary})


from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Count, Q

from books.models import Book

User = get_user_model()


def manager_required(view_func):
    """
    Allow only logged-in managers.
    """

    @login_required
    def wrapper(request, *args, **kwargs):

        if request.user.user_type != "manager":
            raise PermissionDenied(
                "Only managers can access this page."
            )

        return view_func(request, *args, **kwargs)

    return wrapper


@manager_required
def tutor_books(request, tutor_id):
    """
    View all books belonging to one tutor.

    Read-only.
    """

    tutor = get_object_or_404(
        User,
        id=tutor_id,
        user_type="tutor"
    )

    books = (
        Book.objects
        .filter(tutor=tutor)
        .order_by("-created_at")
    )

    context = {
        "tutor": tutor,
        "books": books,
    }

    return render(
        request,
        "manager/tutor_books.html",
        context
    )


@manager_required
def manager_books(request):
    """
    View all books in the library.

    Read-only.
    """

    query = request.GET.get("q", "").strip()

    books = Book.objects.select_related("tutor")

    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(tutor__username__icontains=query) |
            Q(tutor__first_name__icontains=query) |
            Q(tutor__last_name__icontains=query)
        )

    books = books.order_by("-created_at")

    context = {
        "books": books,
        "query": query,
    }

    return render(
        request,
        "manager/books.html",
        context
    )