from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class FrontendAuthenticationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.password = "SecurePass123!"
        cls.user = get_user_model().objects.create_user(
            username="frontenduser",
            password=cls.password,
            role="operador",
        )
        cls.protected_urls = [
            reverse("dashboard"),
            reverse("inventory"),
            reverse("products"),
            reverse("categories"),
            reverse("suppliers"),
            reverse("movements"),
            reverse("restock"),
            reverse("alerts"),
        ]

    def test_register_page_renders_public_template_and_fields(self):
        response = self.client.get(reverse("register"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "inventory_app/register.html")
        self.assertContains(response, "Crear cuenta")
        self.assertContains(response, 'placeholder="Usuario"')
        self.assertContains(response, 'placeholder="Correo electrónico"')
        self.assertContains(response, 'placeholder="Contraseña"')
        self.assertContains(response, 'placeholder="Confirmar contraseña"')

    def test_register_post_creates_admin_user_and_logs_in(self):
        username = "newadmin"
        password = "SecurePass123!"

        response = self.client.post(
            reverse("register"),
            {
                "username": username,
                "email": "newadmin@example.com",
                "password1": password,
                "password2": password,
            },
        )

        self.assertRedirects(response, reverse("dashboard"))

        user = get_user_model().objects.get(username=username)
        self.assertEqual(user.role, "admin")
        self.assertTrue(user.is_staff)

        dashboard_response = self.client.get(reverse("dashboard"))
        self.assertEqual(dashboard_response.status_code, 200)

    def test_register_post_rejects_password_mismatch(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "invalidadmin",
                "email": "invalidadmin@example.com",
                "password1": "SecurePass123!",
                "password2": "DifferentPass123!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "inventory_app/register.html")
        self.assertContains(response, "The two password fields didn’t match.")
        self.assertFalse(get_user_model().objects.filter(username="invalidadmin").exists())

    def test_protected_pages_redirect_anonymous_user_to_login(self):
        for url in self.protected_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(
                    response,
                    f"{reverse('login')}?next={url}",
                    fetch_redirect_response=False,
                )

    def test_authenticated_user_can_access_protected_pages(self):
        self.client.force_login(self.user)

        for url in self.protected_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_login_post_with_valid_credentials_redirects_to_dashboard(self):
        response = self.client.post(
            reverse("login"),
            {"username": self.user.username, "password": self.password},
        )

        self.assertRedirects(response, reverse("dashboard"))

    def test_login_post_with_valid_credentials_honors_next_parameter(self):
        target_url = reverse("inventory")
        response = self.client.post(
            f"{reverse('login')}?next={target_url}",
            {"username": self.user.username, "password": self.password},
        )

        self.assertRedirects(response, target_url)

    def test_logout_redirects_to_login_page(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse("logout"))

        self.assertRedirects(response, reverse("login"))

    def test_user_is_logged_out_after_logout_and_redirected_on_next_private_page(self):
        self.client.force_login(self.user)
        self.client.post(reverse("logout"))

        response = self.client.get(reverse("dashboard"))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('dashboard')}",
            fetch_redirect_response=False,
        )
