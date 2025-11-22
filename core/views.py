from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect

from .models import TodoItem


class HomeView(ListView):
    """Display all TODO items on the home page."""
    model = TodoItem
    template_name = 'home.html'
    context_object_name = 'todos'
    ordering = ['-created_at']


class TodoCreateView(CreateView):
    """Create a new TODO item."""
    model = TodoItem
    template_name = 'todo_form.html'
    fields = ['title', 'description']
    success_url = reverse_lazy('core:home')


class TodoUpdateView(UpdateView):
    """Update an existing TODO item."""
    model = TodoItem
    template_name = 'todo_form.html'
    fields = ['title', 'description', 'completed']
    success_url = reverse_lazy('core:home')


class TodoDeleteView(DeleteView):
    """Delete a TODO item."""
    model = TodoItem
    template_name = 'todo_confirm_delete.html'
    success_url = reverse_lazy('core:home')


class TodoToggleView(View):
    """Toggle the completion status of a TODO item."""
    def post(self, request, pk):
        todo = get_object_or_404(TodoItem, pk=pk)
        todo.completed = not todo.completed
        todo.save()
        return redirect('core:home')
    template_name = 'todo_confirm_delete.html'
    success_url = reverse_lazy('core:home')
