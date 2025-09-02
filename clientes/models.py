# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Asistecias(models.Model):
    id_asistencia = models.AutoField(db_column='ID_ASISTENCIA', primary_key=True)  # Field name made lowercase.
    id_membresia = models.ForeignKey('Membresias', models.DO_NOTHING, db_column='ID_MEMBRESIA')  # Field name made lowercase.
    fecha_asistencia = models.DateField(db_column='Fecha_asistencia')  # Field name made lowercase.
    hora_entrada = models.TimeField(db_column='Hora_entrada')  # Field name made lowercase.
    hora_salida = models.TimeField(db_column='Hora_Salida', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Asistecias'


class Cajas(models.Model):
    id_caja = models.AutoField(db_column='ID_CAJA', primary_key=True)  # Field name made lowercase.
    fecha_hora_apertura = models.DateTimeField(db_column='Fecha_hora_apertura')  # Field name made lowercase.
    fecha_hora_cierre = models.DateTimeField(db_column='Fecha_hora_cierre', blank=True, null=True)  # Field name made lowercase.
    monto_inicial = models.DecimalField(db_column='Monto_inicial', max_digits=12, decimal_places=0)  # Field name made lowercase.
    monto_final = models.DecimalField(db_column='Monto_final', max_digits=12, decimal_places=0, blank=True, null=True)  # Field name made lowercase.
    id_usuario = models.ForeignKey('AuthUser', models.DO_NOTHING, db_column='ID_USUARIO', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Cajas'


class Cobros(models.Model):
    id_cobro = models.AutoField(db_column='ID_COBRO', primary_key=True)  # Field name made lowercase.
    id_cliente = models.ForeignKey('Clientes', models.DO_NOTHING, db_column='ID_CLIENTE')  # Field name made lowercase.
    id_caja = models.ForeignKey(Cajas, models.DO_NOTHING, db_column='ID_CAJA')  # Field name made lowercase.
    monto_total = models.DecimalField(db_column='Monto_total', max_digits=10, decimal_places=0)  # Field name made lowercase.
    fecha_hora = models.DateTimeField(db_column='Fecha_hora', blank=True, null=True)  # Field name made lowercase.
    comentario = models.CharField(db_column='Comentario', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Cobros'


class Cobrosxmetodopago(models.Model):
    id_cobro = models.ForeignKey(Cobros, models.DO_NOTHING, db_column='ID_COBRO')
    id_metodo = models.ForeignKey('Metodopago', models.DO_NOTHING, db_column='ID_METODO')
    monto_pago = models.DecimalField(db_column='Monto_Pago', max_digits=8, decimal_places=0)

    class Meta:
        managed = False
        db_table = 'CobrosXMetodoPago'
        unique_together = (('id_cobro', 'id_metodo'),)


class Detallecobros(models.Model):
    id_servicio = models.ForeignKey('Servicios', models.DO_NOTHING, db_column='ID_SERVICIO')  # Field name made lowercase.
    id_cobro = models.ForeignKey(Cobros, models.DO_NOTHING, db_column='ID_COBRO')  # Field name made lowercase.
    monto = models.DecimalField(db_column='Monto', max_digits=10, decimal_places=0, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'DetalleCobros'
        unique_together = (('id_servicio', 'id_cobro'),)


class Estadoxmembresias(models.Model):
    id_estado = models.ForeignKey('Estados', models.DO_NOTHING, db_column='ID_ESTADO')  # Field name made lowercase.
    id_membresia = models.ForeignKey('Membresias', models.DO_NOTHING, db_column='ID_MEMBRESIA')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'EstadoXMembresias'
        unique_together = (('id_estado', 'id_membresia'),)


class Estados(models.Model):
    id_estado = models.IntegerField(db_column='ID_ESTADO', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=20)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Estados'


class Membresias(models.Model):
    id_membresia = models.AutoField(db_column='ID_MEMBRESIA', primary_key=True)  # Field name made lowercase.
    id_cliente = models.ForeignKey('Clientes', models.DO_NOTHING, db_column='ID_CLIENTE')  # Field name made lowercase.
    id_servicio = models.ForeignKey('Servicios', models.DO_NOTHING, db_column='ID_SERVICIO')  # Field name made lowercase.
    fecha_inicio = models.DateField(db_column='Fecha_inicio')  # Field name made lowercase.
    fecha_vencimiento = models.DateField(db_column='Fecha_vencimiento')  # Field name made lowercase.
    clases_restantes = models.IntegerField(db_column='Clases_restantes')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Membresias'


class Metodopago(models.Model):
    id_metodo = models.IntegerField(db_column='ID_METODO', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=20)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'MetodoPago'


class Servicios(models.Model):
    id_servicio = models.IntegerField(db_column='ID_SERVICIO', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=30)  # Field name made lowercase.
    cantidad = models.SmallIntegerField(db_column='Cantidad')  # Field name made lowercase.
    precio = models.DecimalField(db_column='Precio', max_digits=6, decimal_places=0)  # Field name made lowercase.
    activo = models.CharField(db_column='Activo', max_length=8, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Servicios'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class Clientes(models.Model):
    id_cliente = models.AutoField(db_column='ID_CLIENTE', primary_key=True)  # Field name made lowercase.
    dni = models.CharField(db_column='DNI', unique=True, max_length=15)  # Field name made lowercase.
    apellido = models.CharField(db_column='Apellido', max_length=30)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=30)  # Field name made lowercase.
    domicilio = models.CharField(db_column='Domicilio', max_length=60, blank=True, null=True)  # Field name made lowercase.
    contacto = models.CharField(db_column='Contacto', max_length=10, blank=True, null=True)  # Field name made lowercase.
    contactoemergencia = models.CharField(db_column='ContactoEmergencia', max_length=10, blank=True, null=True)  # Field name made lowercase.
    validacion = models.CharField(db_column='Validacion', max_length=2, blank=True, null=True)  # Field name made lowercase.
    fechacreacion = models.DateTimeField(db_column='FechaCreacion', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'clientes'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'

from django.db import models

class Cliente(models.Model):
    dni = models.IntegerField("DNI", unique=True)
    nombre = models.CharField("Nombre", max_length=30)
    apellido = models.CharField("Apellido", max_length=30)
    email = models.EmailField("Email", unique=True, blank=True)
    telefono = models.CharField("Teléfono", max_length=20)
    emergencia = models.CharField("Emergencia", max_length=20, blank=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.dni})"

class AsistenciaCliente(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.cliente.nombre} - {self.fecha_hora.strftime('%d/%m/%Y %H:%M')}"
