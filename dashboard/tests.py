from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from .models import District, UserProfile, Initiative, Task


class AuthAndPermissionsTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create district
        self.d1 = District.objects.create(name="Batticaloa")
        self.d2 = District.objects.create(name="Ampara")
        # Create users and profiles
        self.admin_user = User.objects.create_user("admin1", password="pw")
        UserProfile.objects.create(user=self.admin_user, role="admin")
        self.coord1 = User.objects.create_user("coord1", password="pw")
        UserProfile.objects.create(user=self.coord1, role="coordinator", district=self.d1)
        self.coord2 = User.objects.create_user("coord2", password="pw")
        UserProfile.objects.create(user=self.coord2, role="coordinator", district=self.d2)
        # Initiative and task for d1 only
        self.init1 = Initiative.objects.create(
            title="Makerspace",
            description="desc",
            initiative_type="other",
            status="active",
            district=self.d1,
            coordinator=self.coord1.profile,
            start_date=timezone.now().date(),
        )
        self.task1 = Task.objects.create(
            title="Kickoff",
            description="d",
            initiative=self.init1,
            assigned_to=self.coord1.profile,
            created_by=self.coord1.profile,
            priority="high",
            status="in_progress",
            due_date=timezone.now() + timezone.timedelta(days=1),
            progress_percentage=10,
        )

    def test_login_required_redirect(self):
        resp = self.client.get(reverse("dashboard_home"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login/", resp.url)

    def test_admin_sees_all(self):
        self.client.login(username="admin1", password="pw")
        resp = self.client.get(reverse("initiatives_list"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Makerspace")

    def test_coordinator_scoping(self):
        # coord1 (same district) should see initiative
        self.client.login(username="coord1", password="pw")
        resp = self.client.get(reverse("initiatives_list"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Makerspace")
        # coord2 (other district) should not see initiative title in list page
        self.client.logout()
        self.client.login(username="coord2", password="pw")
        resp = self.client.get(reverse("initiatives_list"))
        self.assertEqual(resp.status_code, 200)
        self.assertNotContains(resp, "Makerspace")

    def test_update_task_status_api(self):
        self.client.login(username="coord1", password="pw")
        url = reverse("update_task_status", args=[self.task1.pk])
        resp = self.client.post(url, {"status": "completed", "progress": 100})
        self.assertJSONEqual(resp.content, {"success": True})
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.status, "completed")
        self.assertEqual(self.task1.progress_percentage, 100)
        self.assertIsNotNone(self.task1.completed_at)

    def test_task_crud_create_update_delete(self):
        # Coordinator creates a task in their district
        self.client.login(username="coord1", password="pw")
        create_url = reverse("task_create")
        due = (timezone.now() + timezone.timedelta(days=2)).strftime("%Y-%m-%dT%H:%M")
        resp = self.client.post(create_url, {
            "title": "New Task",
            "description": "desc",
            "initiative": self.init1.pk,
            "assigned_to": self.coord1.profile.pk,
            "priority": "medium",
            "status": "not_started",
            "due_date": due,
            "progress_percentage": 0,
        })
        self.assertEqual(resp.status_code, 302)
        task = Task.objects.get(title="New Task")

        # Update as the same coordinator
        update_url = reverse("task_update", args=[task.pk])
        resp = self.client.post(update_url, {
            "title": "New Task Updated",
            "description": "desc2",
            "initiative": self.init1.pk,
            "assigned_to": self.coord1.profile.pk,
            "priority": "high",
            "status": "in_progress",
            "due_date": due,
            "progress_percentage": 50,
        })
        self.assertEqual(resp.status_code, 302)
        task.refresh_from_db()
        self.assertEqual(task.title, "New Task Updated")
        self.assertEqual(task.priority, "high")

        # Delete as admin
        self.client.logout()
        self.client.login(username="admin1", password="pw")
        delete_url = reverse("task_delete", args=[task.pk])
        resp = self.client.post(delete_url)
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Task.objects.filter(pk=task.pk).exists())


# Create your tests here.
