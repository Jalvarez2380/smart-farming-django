from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Parcela(models.Model):
    nombre = models.CharField(max_length=100)
    ubicacion = models.CharField('ubicación', max_length=200)
    descripcion = models.TextField('descripción', blank=True)

    class Meta:
        ordering = ['nombre', 'pk']

    def __str__(self):
        return self.nombre


class Sensor(models.Model):
    class Tipo(models.TextChoices):
        HUMEDAD = 'HUMEDAD', 'Humedad'
        TEMPERATURA = 'TEMPERATURA', 'Temperatura'
        RADIACION = 'RADIACION', 'Radiación'

    class Estado(models.TextChoices):
        ACTIVO = 'ACTIVO', 'Activo'
        INACTIVO = 'INACTIVO', 'Inactivo'

    codigo = models.CharField('código', max_length=50, unique=True)
    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    unidad = models.CharField(max_length=20, help_text='Humedad: %, temperatura: °C, radiación: W/m².')
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.ACTIVO)
    parcela = models.ForeignKey(Parcela, on_delete=models.PROTECT, related_name='sensores')

    class Meta:
        ordering = ['codigo']

    def clean(self):
        super().clean()
        if self.tipo == self.Tipo.HUMEDAD and self.unidad != '%':
            raise ValidationError({'unidad': 'La humedad debe expresarse en %.'})

    def __str__(self):
        return f'{self.codigo} · {self.get_tipo_display()} ({self.unidad})'


class Medicion(models.Model):
    sensor = models.ForeignKey(Sensor, on_delete=models.PROTECT, related_name='mediciones')
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_hora = models.DateTimeField('fecha y hora', auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-fecha_hora', '-pk']
        verbose_name = 'medición'
        verbose_name_plural = 'mediciones'

    @property
    def humedad_baja(self):
        return self.sensor.tipo == Sensor.Tipo.HUMEDAD and self.valor < settings.UMBRAL_HUMEDAD_BAJA

    def clean(self):
        super().clean()
        if not self.sensor_id:
            return
        if self._state.adding and self.sensor.estado != Sensor.Estado.ACTIVO:
            raise ValidationError({'sensor': 'Seleccione un sensor activo.'})
        if self.valor is None or not self.valor.is_finite():
            raise ValidationError({'valor': 'Ingrese un número decimal finito.'})
        if self.sensor.tipo == Sensor.Tipo.HUMEDAD and not 0 <= self.valor <= 100:
            raise ValidationError({'valor': 'La humedad debe estar entre 0 y 100 %.'})
        if self.sensor.tipo == Sensor.Tipo.RADIACION and self.valor < 0:
            raise ValidationError({'valor': 'La radiación no puede ser negativa.'})

    def __str__(self):
        return f'{self.sensor.codigo}: {self.valor} {self.sensor.unidad}'
