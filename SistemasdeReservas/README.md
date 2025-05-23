# Sistema de Reservas

Un sistema de gestión de reservas desarrollado con Flask y SQLite, ideal para pequeños negocios que necesiten administrar citas y servicios.

## Características

- **Interfaz amigable e intuitiva** para la navegación y reserva de servicios
- **Sistema de autenticación y control de roles** (clientes, empleados, administradores)
- **Panel administrativo completo** para gestionar servicios, personal, horarios y reservas
- **Notificaciones automáticas** para confirmación y recordatorio de citas
- **Visualización de disponibilidad en tiempo real** con calendario interactivo
- **Base de datos SQLite** para almacenamiento eficiente y fácil mantenimiento
- **Despliegue web** con tecnologías modernas y multiplataforma

## Requisitos previos

- Python 3.7 o superior
- pip (gestor de paquetes de Python)

## Instalación

1. Clonar el repositorio o descargar los archivos del proyecto:

```bash
git clone https://github.com/juandiegovm/sistema-reservas.git
cd sistema-reservas
```

2. Crear un entorno virtual (opcional pero recomendado):

```bash
python -m venv venv
```

3. Activar el entorno virtual:

- En Windows:
```bash
venv\Scripts\activate
```

- En macOS/Linux:
```bash
source venv/bin/activate
```



4. Instalar las dependencias:

```bash
pip install flask werkzeug
```

## Estructura del proyecto

```
sistema-reservas/
├── app.py                 # Aplicación principal
├── instance/              # Directorio para la base de datos
│   └── reservas.db        # Base de datos SQLite (se crea automáticamente)
├── templates/             # Plantillas HTML
│   ├── base.html          # Plantilla base
│   ├── index.html         # Página de inicio
│   ├── login.html         # Página de inicio de sesión
│   ├── registro.html      # Página de registro
│   ├── cliente_dashboard.html  # Panel de cliente
│   ├── nueva_reserva.html      # Formulario de nueva reserva
│   ├── admin_dashboard.html    # Panel de administrador
│   └── admin_servicios.html    # Gestión de servicios
└── README.md              # Este archivo
```

## Ejecución

Para ejecutar la aplicación:

```bash
python app.py
```

Luego, abre tu navegador y visita [http://localhost:5000](http://localhost:5000)

## Credenciales por defecto

Al iniciar la aplicación por primera vez, se crea automáticamente un usuario administrador:

- **Email**: admin@example.com
- **Contraseña**: admin123

## Personalización

Este proyecto está diseñado para ser sencillo y fácil de modificar. Puedes personalizarlo según tus necesidades específicas:

- Añadir más campos a los servicios
- Implementar un sistema de pagos
- Ampliar las notificaciones a SMS o WhatsApp
- Añadir estadísticas y reportes avanzados
- Personalizar el diseño y la experiencia de usuario

## Uso académico

Este proyecto está diseñado como una base para trabajos universitarios y proyectos educativos. No está pensado para uso en producción sin las correspondientes mejoras de seguridad y escalabilidad.

## Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.
