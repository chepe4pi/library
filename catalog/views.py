from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic import CreateView, TemplateView
from .models import Book
from django.urls import reverse


# Create your views here.

class IndexView(TemplateView):
    template_name = 'catalog/index.html'


class AddBookView(CreateView):
    model = Book
    template_name = 'catalog/book_create.html'
    fields = ['title', 'title_original', 'author', 'categories']

    def get_success_url(self):
        return reverse('index')
