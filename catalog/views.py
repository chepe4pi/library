from django.shortcuts import render
from django.views.generic.list import ListView
from .models import Book


# Create your views here.

class IndexView(ListView):
    model = Book
    template_name = 'catalog/index.html'
    context_object_name = 'books'
