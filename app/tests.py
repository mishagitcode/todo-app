from datetime import timedelta

from django.contrib.admin.sites import site
from django.test import TestCase
from django.urls import resolve, reverse
from django.utils import timezone

from app.admin import TagAdmin, TaskAdmin
from app.forms import DateTimeInput, TagForm, TaskForm
from app.models import Tag, Task
from app.views import (
    TagCreateView,
    TagDeleteView,
    TagListView,
    TagUpdateView,
    TaskCreateView,
    TaskDeleteView,
    TaskListView,
    TaskUpdateView,
    toggle_task_status,
)


class ModelTests(TestCase):
    def test_tag_string_representation_absolute_url_and_ordering(self):
        second_tag = Tag.objects.create(name="Work")
        first_tag = Tag.objects.create(name="Home")

        self.assertEqual(str(first_tag), "Home")
        self.assertEqual(first_tag.get_absolute_url(), reverse("app:tag-list"))
        self.assertEqual(
            list(Tag.objects.values_list("name", flat=True)),
            ["Home", "Work"],
        )
        self.assertEqual(str(second_tag), "Work")

    def test_task_string_representation_absolute_url_and_ordering(self):
        later_task = Task.objects.create(
            content="Later task",
            deadline=timezone.now() + timedelta(days=2),
        )
        earlier_task = Task.objects.create(
            content="Earlier task",
            deadline=timezone.now() + timedelta(days=1),
        )
        completed_task = Task.objects.create(
            content="Completed task",
            deadline=timezone.now() + timedelta(hours=12),
            is_done=True,
        )
        long_content_task = Task.objects.create(content="x" * 60)

        self.assertEqual(str(long_content_task), "x" * 50)
        self.assertEqual(earlier_task.get_absolute_url(), reverse("app:task-list"))
        self.assertEqual(
            list(Task.objects.values_list("id", flat=True)),
            [long_content_task.id, earlier_task.id, later_task.id, completed_task.id],
        )


class FormAndAdminTests(TestCase):
    def test_task_form_widgets_and_validation(self):
        urgent_tag = Tag.objects.create(name="Urgent")
        home_tag = Tag.objects.create(name="Home")
        form = TaskForm(
            data={
                "content": "Buy groceries",
                "deadline": "2026-03-20 10:30:00",
                "tags": [urgent_tag.id, home_tag.id],
            }
        )

        self.assertEqual(DateTimeInput.input_type, "datetime-local")
        self.assertEqual(form.fields["content"].widget.attrs["class"], "form-control")
        self.assertEqual(form.fields["content"].widget.attrs["rows"], 3)
        self.assertEqual(form.fields["deadline"].widget.attrs["class"], "form-control")
        self.assertTrue(form.is_valid(), form.errors)

        task = form.save()

        self.assertEqual(task.tags.count(), 2)

    def test_tag_form_widget_and_validation(self):
        form = TagForm(data={"name": "Personal"})

        self.assertEqual(form.fields["name"].widget.attrs["class"], "form-control")
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().name, "Personal")

    def test_admin_configuration(self):
        self.assertIsInstance(site._registry[Task], TaskAdmin)
        self.assertIsInstance(site._registry[Tag], TagAdmin)
        self.assertEqual(
            site._registry[Task].list_display,
            ("id", "content", "is_done", "created_at", "deadline"),
        )
        self.assertEqual(site._registry[Task].filter_horizontal, ("tags",))
        self.assertEqual(site._registry[Tag].search_fields, ("name",))


class UrlTests(TestCase):
    def test_urls_resolve_to_expected_views(self):
        self.assertEqual(resolve(reverse("app:task-list")).func.view_class, TaskListView)
        self.assertEqual(
            resolve(reverse("app:task-create")).func.view_class,
            TaskCreateView,
        )
        self.assertEqual(
            resolve(reverse("app:task-update", args=[1])).func.view_class,
            TaskUpdateView,
        )
        self.assertEqual(
            resolve(reverse("app:task-delete", args=[1])).func.view_class,
            TaskDeleteView,
        )
        self.assertEqual(
            resolve(reverse("app:task-toggle", args=[1])).func,
            toggle_task_status,
        )
        self.assertEqual(resolve(reverse("app:tag-list")).func.view_class, TagListView)
        self.assertEqual(
            resolve(reverse("app:tag-create")).func.view_class,
            TagCreateView,
        )
        self.assertEqual(
            resolve(reverse("app:tag-update", args=[1])).func.view_class,
            TagUpdateView,
        )
        self.assertEqual(
            resolve(reverse("app:tag-delete", args=[1])).func.view_class,
            TagDeleteView,
        )


class TaskViewTests(TestCase):
    def setUp(self):
        self.home_tag = Tag.objects.create(name="Home")
        self.work_tag = Tag.objects.create(name="Work")
        self.pending_task = Task.objects.create(
            content="Finish Django homework",
            deadline=timezone.now() + timedelta(days=1),
        )
        self.pending_task.tags.set([self.home_tag, self.work_tag])
        self.completed_task = Task.objects.create(
            content="Submit project",
            deadline=timezone.now() + timedelta(days=2),
            is_done=True,
        )
        self.completed_task.tags.set([self.work_tag])

    def test_task_list_view_uses_template_and_ordering(self):
        response = self.client.get(reverse("app:task-list"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "todo/task_list.html")
        self.assertContains(response, "TODO list")
        self.assertContains(response, "Finish Django homework")
        self.assertContains(response, "Submit project")
        self.assertContains(response, "Not done")
        self.assertContains(response, "Done")
        self.assertContains(response, "Complete")
        self.assertContains(response, "Undo")
        self.assertEqual(
            list(response.context["task_list"]),
            [self.pending_task, self.completed_task],
        )

    def test_task_create_view_renders_and_creates_task(self):
        get_response = self.client.get(reverse("app:task-create"))

        self.assertEqual(get_response.status_code, 200)
        self.assertTemplateUsed(get_response, "todo/task_form.html")
        self.assertContains(get_response, "Create task")

        post_response = self.client.post(
            reverse("app:task-create"),
            {
                "content": "Buy milk",
                "deadline": "2026-03-18 08:15:00",
                "tags": [self.home_tag.id],
            },
        )

        self.assertRedirects(post_response, reverse("app:task-list"))
        created_task = Task.objects.get(content="Buy milk")
        self.assertEqual(created_task.deadline.strftime("%Y-%m-%d %H:%M:%S"), "2026-03-18 08:15:00")
        self.assertEqual(list(created_task.tags.all()), [self.home_tag])

    def test_task_update_view_renders_and_updates_task(self):
        get_response = self.client.get(
            reverse("app:task-update", args=[self.pending_task.id])
        )

        self.assertEqual(get_response.status_code, 200)
        self.assertTemplateUsed(get_response, "todo/task_form.html")
        self.assertContains(get_response, "Update task")

        post_response = self.client.post(
            reverse("app:task-update", args=[self.pending_task.id]),
            {
                "content": "Finish updated Django homework",
                "deadline": "2026-03-19 09:45:00",
                "tags": [self.work_tag.id],
            },
        )

        self.assertRedirects(post_response, reverse("app:task-list"))
        self.pending_task.refresh_from_db()
        self.assertEqual(self.pending_task.content, "Finish updated Django homework")
        self.assertEqual(
            self.pending_task.deadline.strftime("%Y-%m-%d %H:%M:%S"),
            "2026-03-19 09:45:00",
        )
        self.assertEqual(list(self.pending_task.tags.all()), [self.work_tag])

    def test_task_delete_view_renders_and_deletes_task(self):
        get_response = self.client.get(
            reverse("app:task-delete", args=[self.completed_task.id])
        )

        self.assertEqual(get_response.status_code, 200)
        self.assertTemplateUsed(get_response, "todo/task_confirm_delete.html")
        self.assertContains(get_response, "Delete task")

        post_response = self.client.post(
            reverse("app:task-delete", args=[self.completed_task.id])
        )

        self.assertRedirects(post_response, reverse("app:task-list"))
        self.assertFalse(Task.objects.filter(id=self.completed_task.id).exists())

    def test_toggle_task_status_switches_value_and_redirects(self):
        first_response = self.client.get(
            reverse("app:task-toggle", args=[self.pending_task.id])
        )

        self.assertRedirects(first_response, reverse("app:task-list"))
        self.pending_task.refresh_from_db()
        self.assertTrue(self.pending_task.is_done)

        second_response = self.client.get(
            reverse("app:task-toggle", args=[self.pending_task.id])
        )

        self.assertRedirects(second_response, reverse("app:task-list"))
        self.pending_task.refresh_from_db()
        self.assertFalse(self.pending_task.is_done)

    def test_toggle_task_status_returns_404_for_missing_task(self):
        response = self.client.get(reverse("app:task-toggle", args=[9999]))

        self.assertEqual(response.status_code, 404)


class TagViewTests(TestCase):
    def setUp(self):
        self.home_tag = Tag.objects.create(name="Home")
        self.work_tag = Tag.objects.create(name="Work")

    def test_tag_list_view_uses_template_and_ordering(self):
        response = self.client.get(reverse("app:tag-list"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "todo/tag_list.html")
        self.assertContains(response, "Tags")
        self.assertEqual(list(response.context["tag_list"]), [self.home_tag, self.work_tag])

    def test_tag_create_view_renders_and_creates_tag(self):
        get_response = self.client.get(reverse("app:tag-create"))

        self.assertEqual(get_response.status_code, 200)
        self.assertTemplateUsed(get_response, "todo/tag_form.html")
        self.assertContains(get_response, "Create tag")

        post_response = self.client.post(
            reverse("app:tag-create"),
            {"name": "Personal"},
        )

        self.assertRedirects(post_response, reverse("app:tag-list"))
        self.assertTrue(Tag.objects.filter(name="Personal").exists())

    def test_tag_update_view_renders_and_updates_tag(self):
        get_response = self.client.get(reverse("app:tag-update", args=[self.home_tag.id]))

        self.assertEqual(get_response.status_code, 200)
        self.assertTemplateUsed(get_response, "todo/tag_form.html")
        self.assertContains(get_response, "Update tag")

        post_response = self.client.post(
            reverse("app:tag-update", args=[self.home_tag.id]),
            {"name": "Family"},
        )

        self.assertRedirects(post_response, reverse("app:tag-list"))
        self.home_tag.refresh_from_db()
        self.assertEqual(self.home_tag.name, "Family")

    def test_tag_delete_view_renders_and_deletes_tag(self):
        get_response = self.client.get(reverse("app:tag-delete", args=[self.work_tag.id]))

        self.assertEqual(get_response.status_code, 200)
        self.assertTemplateUsed(get_response, "todo/tag_confirm_delete.html")
        self.assertContains(get_response, 'Are you sure you want to delete tag "Work"?')

        post_response = self.client.post(reverse("app:tag-delete", args=[self.work_tag.id]))

        self.assertRedirects(post_response, reverse("app:tag-list"))
        self.assertFalse(Tag.objects.filter(id=self.work_tag.id).exists())
