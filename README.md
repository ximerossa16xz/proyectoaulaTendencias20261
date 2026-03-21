# inventary
# Inventory API (Django REST Framework)

## Descripción

Este proyecto consiste en el desarrollo de una API para la gestión de inventario utilizando **Django** y **Django REST Framework**. Permite administrar:

* Categorías
* Proveedores
* Productos

El sistema implementa un esquema de autenticación con diferenciación de roles:

* Administrador: acceso completo a las operaciones del sistema.
* Operador: acceso restringido únicamente a consultas.

---

## Tecnologías utilizadas

* Python
* Django
* Django REST Framework
* SQLite

---

## Ejecución del proyecto

1. Activar el entorno virtual:

```bash
source venv/Scripts/activate
```

2. Instalar dependencias:

```bash
pip install django djangorestframework
```

3. Ejecutar migraciones:

```bash
python manage.py makemigrations
python manage.py migrate
```

4. Crear superusuario:

```bash
python manage.py createsuperuser
```

5. Ejecutar el servidor:

```bash
python manage.py runserver
```

6. Acceder a la aplicación:

```
http://127.0.0.1:8000/
```

---

## Autenticación

El sistema utiliza autenticación por sesión de Django.

Ruta de acceso:

```
http://127.0.0.1:8000/api-auth/login/
```

---

## Roles del sistema

| Rol           | Permisos                            |
| ------------- | ----------------------------------- |
| Administrador | Crear, editar, eliminar y consultar |
| Operador      | Consultar (GET) únicamente          |

---

## Endpoints disponibles

### Categorías

* GET `/api/categories/`
* POST `/api/categories/`
* GET `/api/categories/{id}/`
* PUT/PATCH `/api/categories/{id}/`
* DELETE `/api/categories/{id}/`

---

### Proveedores

* GET `/api/suppliers/`
* POST `/api/suppliers/`
* GET `/api/suppliers/{id}/`
* PUT/PATCH `/api/suppliers/{id}/`
* DELETE `/api/suppliers/{id}/`

---

### Productos

* GET `/api/products/`
* POST `/api/products/`
* GET `/api/products/{id}/`
* PUT/PATCH `/api/products/{id}/`
* DELETE `/api/products/{id}/`

---

## Ejemplos de uso

### Crear categoría

```json
{
  "name": "Electrónica",
  "description": "Productos tecnológicos",
  "status": "active"
}
```

### Crear proveedor

```json
{
  "name": "Proveedor Central",
  "nit": "900123456",
  "contact": "Juan Pérez",
  "email": "proveedor@email.com",
  "phone": "3001234567"
}
```

### Crear producto

```json
{
  "name": "Teclado",
  "sku": "TEC-001",
  "category": 1,
  "supplier": 1,
  "unit_measure": "unidad",
  "cost_price": "100000.00",
  "sale_price": "150000.00",
  "stock": 10,
  "minimum_stock": 2
}
```

---

## Validaciones implementadas

* El campo SKU es único para cada producto.
* Se requiere el diligenciamiento de los campos obligatorios.
* Se mantiene la integridad referencial entre productos, categorías y proveedores.

---

## Control de acceso

Se implementaron permisos personalizados que permiten:

* Restringir el acceso a usuarios no autenticados.
* Limitar a los operadores a operaciones de consulta.
* Permitir a los administradores el acceso completo al sistema.

---

## Estructura del proyecto

```
inventory/
│
├── accounts/
├── inventory_app/
├── config/
├── manage.py
└── venv/
```

---

## Conclusión

El sistema desarrollado cumple con los requerimientos establecidos, incluyendo:

* Estructura organizada del proyecto
* API funcional basada en Django REST Framework
* Control de acceso mediante roles
* Validación de datos
* Relaciones entre entidades del sistema

---

## Autor

Proyecto académico desarrollado como parte de un taller de Django REST Framework.
