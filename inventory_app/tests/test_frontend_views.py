from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class FrontendViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.password = "SecurePass123!"
        cls.user = get_user_model().objects.create_user(
            username="operador",
            password=cls.password,
            role="operador",
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_login_page_renders_public_template_and_fields(self):
        self.client.logout()

        response = self.client.get(reverse("login"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "inventory_app/login.html")
        self.assertContains(response, "<title>Login</title>", html=True)
        self.assertContains(response, 'placeholder="Usuario"')
        self.assertContains(response, 'placeholder="Contrasena"')
        self.assertContains(response, "Ingresar")

    def test_dashboard_page_renders_expected_template_and_content(self):
        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "inventory_app/index.html")
        self.assertContains(response, "Panel central de inventario")
        self.assertContains(response, "Control operativo")
        self.assertContains(response, "Ver historial")
        self.assertContains(response, "Accesos rapidos")

    def test_inventory_page_renders_expected_template_and_content(self):
        response = self.client.get(reverse("inventory"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "inventory_app/inventory.html")
        self.assertContains(response, "Inventario general")
        self.assertContains(response, "Vista de inventario")
        self.assertContains(response, "Prioridades de reposicion")
        self.assertContains(response, "Ver productos")

    def test_products_page_renders_expected_template_and_visible_controls(self):
        response = self.client.get(reverse("products"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "inventory_app/products.html")
        self.assertContains(response, "Productos")
        self.assertContains(response, "Buscar por nombre o SKU")
        self.assertContains(response, "Lista de productos")
        self.assertContains(response, "Estadisticas")
        self.assertNotContains(response, "Agregar producto")

    def test_categories_page_renders_expected_template_and_visible_controls(self):
        response = self.client.get(reverse("categories"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "inventory_app/categories.html")
        self.assertContains(response, "Categorias")
        self.assertContains(response, "Lista de categorias")
        self.assertContains(response, "Estadisticas")
        self.assertNotContains(response, "Agregar categoria")

    def test_suppliers_page_renders_expected_template_and_visible_controls(self):
        response = self.client.get(reverse("suppliers"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "inventory_app/suppliers.html")
        self.assertContains(response, "Proveedores")
        self.assertContains(response, "Lista de Proveedores")
        self.assertNotContains(response, 'id="new-supplier-btn"')

    def test_movements_page_renders_expected_template_and_content(self):
        response = self.client.get(reverse("movements"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "inventory_app/movements.html")
        self.assertContains(response, "Movimientos de inventario")
        self.assertContains(response, "Historial de movimientos")
        self.assertContains(response, "Cargando movimientos")

    def test_restock_page_renders_expected_template_and_content(self):
        response = self.client.get(reverse("restock"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "inventory_app/restock.html")
        self.assertContains(response, "Listado de")
        self.assertContains(response, "Cargando")
        self.assertContains(response, "Producto")

    def test_alerts_page_renders_expected_template_and_content(self):
        response = self.client.get(reverse("alerts"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "inventory_app/alerts.html")
        self.assertContains(response, "Alertas")
        self.assertContains(response, "Cargando alertas")
        self.assertContains(response, "Stock")

    def test_admin_user_sees_management_buttons_in_frontend(self):
        admin_user = get_user_model().objects.create_user(
            username="admin_front",
            password=self.password,
            role="admin",
            is_staff=True,
        )
        self.client.force_login(admin_user)

        products_response = self.client.get(reverse("products"))
        categories_response = self.client.get(reverse("categories"))
        suppliers_response = self.client.get(reverse("suppliers"))

        self.assertContains(products_response, "Agregar producto")
        self.assertContains(categories_response, "Agregar categoria")
        self.assertContains(suppliers_response, "Nuevo proveedor")
