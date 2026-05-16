from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class FrontendFormsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.password = "SecurePass123!"
        cls.user = get_user_model().objects.create_user(
            username="formuser",
            password=cls.password,
            role="operador",
        )

    def test_login_form_renders_visible_fields_and_submit_button(self):
        response = self.client.get(reverse("login"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<form", count=1)
        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="password"')
        self.assertContains(response, "Ingresar")

    def test_login_form_invalid_submission_shows_error_message_in_html(self):
        response = self.client.post(
            reverse("login"),
            {"username": self.user.username, "password": "wrong-password"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "inventory_app/login.html")
        self.assertContains(response, "Please enter a correct username and password")
        self.assertContains(response, "Ingresar")

    def test_login_form_valid_submission_redirects_user(self):
        response = self.client.post(
            reverse("login"),
            {"username": self.user.username, "password": self.password},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("dashboard"))

    def test_admin_frontend_forms_are_visible_in_rendered_templates(self):
        admin_user = get_user_model().objects.create_user(
            username="adminforms",
            password=self.password,
            role="admin",
            is_staff=True,
        )
        self.client.force_login(admin_user)

        products_response = self.client.get(reverse("products"))
        categories_response = self.client.get(reverse("categories"))
        suppliers_response = self.client.get(reverse("suppliers"))

        self.assertContains(products_response, 'id="product-form"')
        self.assertContains(products_response, "Guardar")
        self.assertContains(categories_response, 'id="category-form"')
        self.assertContains(categories_response, "Guardar")
        self.assertContains(suppliers_response, 'id="supplier-form"')
        self.assertContains(suppliers_response, "Guardar")
