from django.apps import AppConfig


class LoginConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'login'
    def ready(self):
        # Importar aquí para evitar problemas de carga circular
        from django.contrib.sessions.models import Session
        try:
            Session.objects.all().delete()
            print("Todas las sesiones eliminadas al iniciar el servidor")
        except Exception as e:
            print(f"Error al limpiar sesiones: {e}")

