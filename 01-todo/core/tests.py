from django.test import Client, TestCase
from django.urls import reverse

from .models import TodoItem


class TodoItemModelTests(TestCase):
    """Tests for the TodoItem model."""

    def setUp(self):
        """Set up test fixtures."""
        self.todo = TodoItem.objects.create(
            title="Test Todo", description="Test Description", completed=False
        )

    def test_todo_creation(self):
        """Test that a TodoItem can be created."""
        self.assertEqual(self.todo.title, "Test Todo")
        self.assertEqual(self.todo.description, "Test Description")
        self.assertFalse(self.todo.completed)

    def test_todo_string_representation(self):
        """Test the string representation of TodoItem."""
        self.assertEqual(str(self.todo), "Test Todo")

    def test_todo_default_completed_is_false(self):
        """Test that new todos are not completed by default."""
        todo = TodoItem.objects.create(title="New Todo")
        self.assertFalse(todo.completed)

    def test_todo_completed_can_be_set_true(self):
        """Test that completed status can be set to True."""
        self.todo.completed = True
        self.todo.save()
        self.assertTrue(self.todo.completed)

    def test_todo_timestamps(self):
        """Test that created_at and updated_at are set."""
        self.assertIsNotNone(self.todo.created_at)
        self.assertIsNotNone(self.todo.updated_at)

    def test_todo_ordering(self):
        """Test that todos are ordered by created_at descending."""
        todo2 = TodoItem.objects.create(title="Second Todo")
        todos = list(TodoItem.objects.all())
        self.assertEqual(todos[0].id, todo2.id)
        self.assertEqual(todos[1].id, self.todo.id)

    def test_todo_description_blank_allowed(self):
        """Test that description can be blank."""
        todo = TodoItem.objects.create(title="No Description Todo")
        self.assertIsNone(todo.description)


class HomeViewTests(TestCase):
    """Tests for the HomeView."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = Client()
        self.url = reverse("core:home")
        self.todo1 = TodoItem.objects.create(title="Todo 1", description="Description 1")
        self.todo2 = TodoItem.objects.create(
            title="Todo 2", description="Description 2", completed=True
        )

    def test_home_view_status_code(self):
        """Test that home view returns 200 status code."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_home_view_template_used(self):
        """Test that home view uses the correct template."""
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "home.html")

    def test_home_view_context(self):
        """Test that home view passes todos in context."""
        response = self.client.get(self.url)
        self.assertIn("todos", response.context)

    def test_home_view_displays_all_todos(self):
        """Test that home view displays all todos."""
        response = self.client.get(self.url)
        todos = response.context["todos"]
        self.assertEqual(len(todos), 2)

    def test_home_view_todos_ordered_by_created_at(self):
        """Test that todos are ordered by created_at descending."""
        response = self.client.get(self.url)
        todos = list(response.context["todos"])
        self.assertEqual(todos[0].id, self.todo2.id)
        self.assertEqual(todos[1].id, self.todo1.id)


class TodoCreateViewTests(TestCase):
    """Tests for the TodoCreateView."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = Client()
        self.create_url = reverse("core:create")
        self.home_url = reverse("core:home")

    def test_create_view_get_status_code(self):
        """Test that create view GET returns 200 status code."""
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)

    def test_create_view_template_used(self):
        """Test that create view uses the correct template."""
        response = self.client.get(self.create_url)
        self.assertTemplateUsed(response, "todo_form.html")

    def test_create_todo_post(self):
        """Test creating a new todo via POST."""
        data = {"title": "New Todo", "description": "New Description"}
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.home_url)
        self.assertTrue(TodoItem.objects.filter(title="New Todo").exists())

    def test_create_todo_without_description(self):
        """Test creating a todo without description."""
        data = {"title": "Todo without description"}
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, 302)
        todo = TodoItem.objects.get(title="Todo without description")
        self.assertEqual(todo.description, "")

    def test_create_todo_required_field(self):
        """Test that title is required."""
        data = {"description": "Description only"}
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)
        self.assertTrue(response.context["form"].errors)


class TodoUpdateViewTests(TestCase):
    """Tests for the TodoUpdateView."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = Client()
        self.todo = TodoItem.objects.create(
            title="Original Title", description="Original Description"
        )
        self.edit_url = reverse("core:edit", kwargs={"pk": self.todo.pk})
        self.home_url = reverse("core:home")

    def test_update_view_get_status_code(self):
        """Test that update view GET returns 200 status code."""
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 200)

    def test_update_view_template_used(self):
        """Test that update view uses the correct template."""
        response = self.client.get(self.edit_url)
        self.assertTemplateUsed(response, "todo_form.html")

    def test_update_todo_post(self):
        """Test updating a todo via POST."""
        data = {
            "title": "Updated Title",
            "description": "Updated Description",
            "completed": True,
        }
        response = self.client.post(self.edit_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.home_url)
        self.todo.refresh_from_db()
        self.assertEqual(self.todo.title, "Updated Title")
        self.assertEqual(self.todo.description, "Updated Description")
        self.assertTrue(self.todo.completed)

    def test_update_nonexistent_todo(self):
        """Test updating a nonexistent todo returns 404."""
        url = reverse("core:edit", kwargs={"pk": 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class TodoDeleteViewTests(TestCase):
    """Tests for the TodoDeleteView."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = Client()
        self.todo = TodoItem.objects.create(title="Todo to Delete", description="Will be deleted")
        self.delete_url = reverse("core:delete", kwargs={"pk": self.todo.pk})
        self.home_url = reverse("core:home")

    def test_delete_view_get_status_code(self):
        """Test that delete view GET returns 200 status code."""
        response = self.client.get(self.delete_url)
        self.assertEqual(response.status_code, 200)

    def test_delete_view_template_used(self):
        """Test that delete view uses the correct template."""
        response = self.client.get(self.delete_url)
        self.assertTemplateUsed(response, "todo_confirm_delete.html")

    def test_delete_todo_post(self):
        """Test deleting a todo via POST."""
        response = self.client.post(self.delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.home_url)
        self.assertFalse(TodoItem.objects.filter(pk=self.todo.pk).exists())

    def test_delete_nonexistent_todo(self):
        """Test deleting a nonexistent todo returns 404."""
        url = reverse("core:delete", kwargs={"pk": 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class TodoToggleViewTests(TestCase):
    """Tests for the TodoToggleView."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = Client()
        self.todo = TodoItem.objects.create(title="Toggle Test Todo", completed=False)
        self.toggle_url = reverse("core:toggle", kwargs={"pk": self.todo.pk})
        self.home_url = reverse("core:home")

    def test_toggle_incomplete_to_complete(self):
        """Test toggling a todo from incomplete to complete."""
        self.assertFalse(self.todo.completed)
        response = self.client.post(self.toggle_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.home_url)
        self.todo.refresh_from_db()
        self.assertTrue(self.todo.completed)

    def test_toggle_complete_to_incomplete(self):
        """Test toggling a todo from complete to incomplete."""
        self.todo.completed = True
        self.todo.save()
        response = self.client.post(self.toggle_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.home_url)
        self.todo.refresh_from_db()
        self.assertFalse(self.todo.completed)

    def test_toggle_nonexistent_todo(self):
        """Test toggling a nonexistent todo returns 404."""
        url = reverse("core:toggle", kwargs={"pk": 9999})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_toggle_get_request_not_allowed(self):
        """Test that GET request is not allowed for toggle."""
        response = self.client.get(self.toggle_url)
        self.assertEqual(response.status_code, 405)
