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

@login_required
def read_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    
    # Fetch existing notes and highlights to display in the sidebar
    notes = BookNote.objects.filter(user=request.user, book=book).order_by('-created_at')
    highlights = Highlight.objects.filter(user=request.user, book=book).order_by('-created_at')
    
    # Retrieve last progress
    progress = ReadingProgress.objects.filter(user=request.user, book=book).first()
    start_page = progress.last_page if progress else 1

    context = {
        'book': book,
        'notes': notes,
        'highlights': highlights,
        'start_page': start_page,
    }
    return render(request, 'books/read.html', context)

    import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import BookNote, Book
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import Book, BookNote, Highlight, Bookmark, ReadingProgress

@login_required
@csrf_exempt
def add_note(request, pk):
    if request.method == 'POST':
        data = json.loads(request.body)
        book = get_object_or_404(Book, pk=pk)
        note = BookNote.objects.create(
            user=request.user, 
            book=book, 
            note=data.get('note', '').strip(),
            page=data.get('page', 1)
        )
        return JsonResponse({'note': note.note, 'page': note.page})


@csrf_exempt
@login_required
def save_highlight(request, pk):
    data = json.loads(request.body)
    text = data.get('text')
    page = data.get('page')

    book = get_object_or_404(Book, pk=pk)

    Highlight.objects.create(
        user=request.user,
        book=book,
        text=text,
        page=page
    )

    return JsonResponse({'status': 'saved'})


from .models import Book, Bookmark  

@login_required
def bookmark_page(request, pk):
    if request.method == "POST":
        data = json.loads(request.body)
        page = data.get("page")

        book = get_object_or_404(Book, pk=pk)

        Bookmark.objects.create(
            user=request.user,
            book=book,
            page=page
        )

        return JsonResponse({"status": "saved"})

    return JsonResponse({"error": "Invalid request"}, status=400)






from .models import Book, ReadingProgress


@login_required
def save_progress(request, pk):
    if request.method == "POST":
        data = json.loads(request.body)
        page = data.get("page")
        book = get_object_or_404(Book, pk=pk)

        # Atomic update or create
        ReadingProgress.objects.update_or_create(
            user=request.user, book=book,
            defaults={'last_page': page}
        )
        return JsonResponse({"status": "saved", "page": page})
    return JsonResponse({"error": "Invalid request"}, status=400)




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