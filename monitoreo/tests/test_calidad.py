from decimal import Decimal
from io import StringIO

from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db.models import ProtectedError
from django.urls import reverse

from monitoreo.forms import MedicionForm
from monitoreo.models import Medicion, Parcela, Sensor

from .base import DatosMonitoreo


class PruebasCalidad(DatosMonitoreo):
    def test_humedad_invalida_no_se_guarda(self):
        for valor in ['-0.01', '100.01', 'abc', '', 'NaN', 'Infinity', '1.001']:
            with self.subTest(valor=valor):
                response = self.client.post(reverse('monitoreo:registrar'), {
                    'sensor': self.sensor.pk, 'valor': valor,
                })
                self.assertEqual(response.status_code, 200)
                self.assertIn('valor', response.context['form'].errors)
        self.assertEqual(Medicion.objects.count(), 0)

    def test_limites_humedad_validos(self):
        for valor in ['0', '100']:
            with self.subTest(valor=valor):
                self.assertTrue(MedicionForm({'sensor': self.sensor.pk, 'valor': valor}).is_valid())

    def test_sensor_inactivo_o_inexistente_rechazado(self):
        self.sensor.estado = Sensor.Estado.INACTIVO
        self.sensor.save()
        for sensor_id in [self.sensor.pk, 99999, 'abc', '']:
            with self.subTest(sensor_id=sensor_id):
                form = MedicionForm({'sensor': sensor_id, 'valor': '20'})
                self.assertFalse(form.is_valid())
                self.assertIn('sensor', form.errors)

    def test_validacion_radiacion_y_temperatura(self):
        self.sensor.tipo = Sensor.Tipo.RADIACION
        self.sensor.unidad = 'W/m²'
        self.sensor.save()
        self.assertFalse(MedicionForm({'sensor': self.sensor.pk, 'valor': '-1'}).is_valid())
        self.sensor.tipo = Sensor.Tipo.TEMPERATURA
        self.sensor.unidad = '°C'
        self.sensor.save()
        self.assertTrue(MedicionForm({'sensor': self.sensor.pk, 'valor': '-1'}).is_valid())

    def test_codigo_unico_y_unidad_humedad(self):
        duplicado = Sensor(codigo=self.sensor.codigo, tipo=Sensor.Tipo.HUMEDAD,
                           unidad='%', parcela=self.parcela)
        with self.assertRaises(ValidationError):
            duplicado.full_clean()
        self.sensor.unidad = '°C'
        with self.assertRaises(ValidationError):
            self.sensor.full_clean()

    def test_filtros_combinados_y_orden(self):
        otra_parcela = Parcela.objects.create(nombre='Maíz', ubicacion='Tena')
        otro_sensor = Sensor.objects.create(codigo='T-01', tipo=Sensor.Tipo.TEMPERATURA,
                                            unidad='°C', parcela=otra_parcela)
        primera = Medicion.objects.create(sensor=self.sensor, valor=Decimal('20'))
        segunda = Medicion.objects.create(sensor=self.sensor, valor=Decimal('21'))
        Medicion.objects.create(sensor=otro_sensor, valor=Decimal('25'))
        response = self.client.get(reverse('monitoreo:historico'), {
            'parcela': self.parcela.pk, 'tipo': Sensor.Tipo.HUMEDAD,
        })
        self.assertEqual(list(response.context['mediciones']), [segunda, primera])
        response = self.client.get(reverse('monitoreo:historico'), {'tipo': 'INVALIDO'})
        self.assertTrue(response.context['form'].errors)
        self.assertEqual(list(response.context['mediciones']), [])

    def test_demo_idempotente(self):
        salida = StringIO()
        call_command('cargar_demo', stdout=salida)
        cantidades = (Parcela.objects.count(), Sensor.objects.count(), Medicion.objects.count())
        self.assertEqual(cantidades, (3, 7, 12))
        call_command('cargar_demo', stdout=salida)
        self.assertEqual(cantidades, (
            Parcela.objects.count(), Sensor.objects.count(), Medicion.objects.count(),
        ))

    def test_proteccion_del_historico(self):
        Medicion.objects.create(sensor=self.sensor, valor=Decimal('20'))
        with self.assertRaises(ProtectedError):
            self.sensor.delete()
        with self.assertRaises(ProtectedError):
            self.parcela.delete()

    def test_paginas_y_estados_vacios(self):
        for pagina in ['dashboard', 'parcelas', 'sensores', 'registrar', 'historico']:
            with self.subTest(pagina=pagina):
                self.assertEqual(self.client.get(reverse(f'monitoreo:{pagina}')).status_code, 200)
        self.assertContains(self.client.get(reverse('monitoreo:historico')), 'No hay mediciones')

    def test_paginacion_conserva_filtros(self):
        Medicion.objects.bulk_create([
            Medicion(sensor=self.sensor, valor=Decimal('40')) for _ in range(21)
        ])
        response = self.client.get(reverse('monitoreo:historico'), {
            'parcela': self.parcela.pk, 'tipo': Sensor.Tipo.HUMEDAD, 'page': 2,
        })
        self.assertEqual(len(response.context['mediciones']), 1)
        self.assertContains(response, 'tipo=HUMEDAD')
