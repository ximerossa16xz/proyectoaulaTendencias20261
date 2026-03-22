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
http://127.0.0.1:8000/admin
```

---

## Autenticación

El sistema utiliza **TokenAuthentication** y **SessionAuthentication**, permitiendo acceso tanto desde Postman como desde el navegador.

### En el Navegador (SessionAuthentication):

Accede a:
```
http://127.0.0.1:8000/api-auth/login/
```

Verás una interfaz HTML amigable donde puedes ingresar tus credenciales. La sesión se mantiene automáticamente.

### En Postman (TokenAuthentication):

Realiza una petición POST a:
```
http://127.0.0.1:8000/api/accounts/login/
```

Envía tus credenciales y obtendrás un token. Luego incluye el token en el header:
```
Authorization: Token <tu_token>
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

---

### Proveedores

* GET `/api/suppliers/`
* POST `/api/suppliers/`
* GET `/api/suppliers/{id}/`

---

### Productos

* GET `/api/products/`
* POST `/api/products/`
* GET `/api/products/{id}/`

---

## Ejemplos de uso

### Login en Postman (Token Authentication)

* POST http://127.0.0.1:8000/api/accounts/login/
* Headers: 
    Content-Type: application/json
* Body: 
    raw JSON
    {
      "username": "tu_usuario",
      "password": "tu_contraseña"
    }

* Respuesta esperada:
  {
    "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
    "user": {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "role": "admin",
      "is_staff": true
    }
  }

### Login en Navegador (Session Authentication)

Para loguearse en el navegador:

1. Accede a: `http://127.0.0.1:8000/api-auth/login/`
2. Ingresa tus credenciales en la interfaz HTML
3. Haz clic en "Log in"
4. La sesión se mantiene automáticamente en las peticiones posteriores

Para cerrar sesión:

1. Haz clic en el botón "Log out" en la parte superior
2. Serás redirigido automáticamente a la página de login

### Dashboard - Ver información y permisos del usuario:

* GET http://127.0.0.1:8000/api/accounts/dashboard/
* Headers: 
    Content-Type: application/json
* Body: 
    raw JSON
    {
      "username": "tu_usuario",
      "password": "tu_contraseña"
    }

* Respuesta esperada:
  {
    "usuario": {
      "perfil": "/api/accounts/profile/",
      "username": "admin",
      "email": "admin@example.com",
      "rol": "admin",
      "es_staff": true
    },
    "endpoints_disponibles": {...},
    "permisos": {...}
  }

### Listar Categorías (Debe estar logueado):

* GET http://127.0.0.1:8000/api/categories/
* Headers: 
    Content-Type: application/json
    Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b

* Respuesta esperada:
  [
      {
          "id": CategoryId,
          "name": "CategoryName",
          "description": "CategoryDescription",
          "status": "active"
      }
  ]

### Crear Categorías (solo admin):

* POST http://127.0.0.1:8000/api/categories/
* Headers: 
    Content-Type: application/json
		Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
* Body: 
    raw JSON
    {
      "name": "Electrónica",
      "description": "Productos electrónicos en general",
      "status": "active"
    }

### Listar Proovedores (Debe estar logueado):

* GET http://127.0.0.1:8000/api/suppliers/
* Headers: 
    Content-Type: application/json
		Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
* Respuesta esperada:
  [
      {
          "id": SupplierId,
          "name": "SupplierTradeName",
          "nit": "SupplierNit",
          "contact": "SupplierName",
          "email": "SupplierEmail",
          "phone": "SupplierPhone"
      }
  ]

### Crear Proovedores (solo admin):

* POST http://127.0.0.1:8000/api/suppliers/
* Headers: 
    Content-Type: application/json
    Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
* Body: 
    raw JSON
    {
      "name": "Distribuidora XYZ",
      "nit": "123456789",
      "contact": "Juan Pérez",
      "email": "contacto@xyz.com",
      "phone": "3001234567"
    }


### Listar Productos (Debe estar logueado):

* GET http://127.0.0.1:8000/api/products/
* Headers: 
    Content-Type: application/json
		Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b

* Respuesta esperada:
  [
      {
          "id": ProductId,
          "name": "ProductName",
          "sku": "ProductSKU",
          "unit_measure": "ProductUnitMeasure",
          "cost_price": "ProductCostPrice",
          "sale_price": "ProductSalePrice",
          "stock": ProductStock,
          "minimum_stock": ProductMinimumStock,
          "category": CategoryId,
          "supplier": SupplierId
      }
  ]

### Crear Productos (solo admin):
* POST http://127.0.0.1:8000/api/products/
* Headers: 
    Content-Type: application/json
    Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
* Body: 
    raw JSON
    {
      "name": "Laptop Dell",
      "sku": "DELL-001",
      "category": 1,
      "supplier": 2,
      "unit_measure": "unidad",
      "cost_price": "800.00",
      "sale_price": "1200.00",
      "stock": 50,
      "minimum_stock": 10
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

* Restringir la creación a usuarios no autenticados.
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
