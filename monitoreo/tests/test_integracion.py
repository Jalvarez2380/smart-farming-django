from decimal import Decimal

from django.urls import reverse

from monitoreo.models import Medicion

from .base import DatosMonitoreo


class PruebasIntegracion(DatosMonitoreo):
    def test_relaciones_en_base_de_datos(self):
        medicion = Medicion.objects.create(sensor=self.sensor, valor=Decimal('23.50'))
        recuperada = Medicion.objects.select_related('sensor__parcela').get(pk=medicion.pk)
        self.assertEqual(recuperada.sensor.parcela, self.parcela)
        self.assertEqual(self.parcela.sensores.get(), self.sensor)
        self.assertEqual(self.sensor.mediciones.get(), recuperada)
        self.assertIsNotNone(recuperada.fecha_hora)

    def test_registro_aparece_en_historico_y_dashboard(self):
        response = self.client.post(reverse('monitoreo:registrar'), {
            'sensor': self.sensor.pk, 'valor': '22.50',
        })
        self.assertRedirects(response, reverse('monitoreo:historico'))
        medicion = Medicion.objects.get()
        for pagina in ['historico', 'dashboard']:
            with self.subTest(pagina=pagina):
                response = self.client.get(reverse(f'monitoreo:{pagina}'))
                self.assertIn(medicion, response.context['mediciones'])
                self.assertContains(response, 'Humedad del suelo baja')
