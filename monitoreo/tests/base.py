from django.test import TestCase

from monitoreo.models import Parcela, Sensor


class DatosMonitoreo(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.parcela = Parcela.objects.create(nombre='Cacao', ubicacion='Puyo')
        cls.sensor = Sensor.objects.create(
            codigo='H-01', tipo=Sensor.Tipo.HUMEDAD, unidad='%', parcela=cls.parcela,
        )
