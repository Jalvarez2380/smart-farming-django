from decimal import Decimal

from django.test import TestCase, override_settings

from monitoreo.models import Medicion, Parcela, Sensor


class PruebasUnitarias(TestCase):
    def test_crear_parcela(self):
        parcela = Parcela.objects.create(nombre='Cacao', ubicacion='Puyo')
        parcela.full_clean()
        parcela.refresh_from_db()
        self.assertEqual(str(parcela), 'Cacao')
        self.assertEqual(parcela.ubicacion, 'Puyo')
        self.assertEqual(parcela.descripcion, '')

    def test_crear_sensor_asociado(self):
        parcela = Parcela.objects.create(nombre='Cacao', ubicacion='Puyo')
        sensor = Sensor.objects.create(
            codigo='H-01', tipo=Sensor.Tipo.HUMEDAD, unidad='%', parcela=parcela,
        )
        sensor.full_clean()
        sensor.refresh_from_db()
        self.assertEqual(sensor.parcela, parcela)
        self.assertEqual(sensor.estado, Sensor.Estado.ACTIVO)
        self.assertIn('H-01', str(sensor))

    @override_settings(UMBRAL_HUMEDAD_BAJA=30)
    def test_detectar_humedad_baja(self):
        sensor = Sensor(tipo=Sensor.Tipo.HUMEDAD)
        for valor, esperado in [('29.99', True), ('30.00', False), ('30.01', False)]:
            with self.subTest(valor=valor):
                self.assertEqual(Medicion(sensor=sensor, valor=Decimal(valor)).humedad_baja, esperado)
        sensor.tipo = Sensor.Tipo.TEMPERATURA
        self.assertFalse(Medicion(sensor=sensor, valor=Decimal('10')).humedad_baja)
        sensor.tipo = Sensor.Tipo.HUMEDAD
        with override_settings(UMBRAL_HUMEDAD_BAJA=40):
            self.assertTrue(Medicion(sensor=sensor, valor=Decimal('35')).humedad_baja)
