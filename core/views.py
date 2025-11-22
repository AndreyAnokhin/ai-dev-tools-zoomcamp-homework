from django.shortcuts import render
from django.views import View
from django.views.generic import ListView

from .models import TodoItem


class HomeView(ListView):
    """Display all TODO items on the home page."""
    model = TodoItem
    template_name = 'home.html'
    context_object_name = 'todos'
    ordering = ['-created_at']
