from django.test import Client, override_settings
from django.urls import reverse

from monitoreo.models import Medicion

from .base import DatosMonitoreo


class PruebaAceptacion(DatosMonitoreo):
    def test_registro_informa_umbral_de_alerta(self):
        for umbral in [30, 40]:
            with self.subTest(umbral=umbral), override_settings(UMBRAL_HUMEDAD_BAJA=umbral):
                respuesta = self.client.get(reverse('monitoreo:registrar'))
                self.assertContains(
                    respuesta,
                    f'Las mediciones de humedad inferiores al {umbral} % generan una alerta '
                    'de humedad del suelo baja.',
                )

    def test_usuario_registra_medicion_valida(self):
        cliente = Client(enforce_csrf_checks=True)
        url = reverse('monitoreo:registrar')
        formulario = cliente.get(url)
        self.assertEqual(formulario.status_code, 200)
        self.assertContains(formulario, 'Guardar medición')
        respuesta = cliente.post(url, {
            'sensor': self.sensor.pk, 'valor': '45.25',
            'csrfmiddlewaretoken': cliente.cookies['csrftoken'].value,
        }, follow=True)
        self.assertRedirects(respuesta, reverse('monitoreo:historico'))
        self.assertContains(respuesta, 'Medición registrada correctamente.')
        self.assertContains(respuesta, '45,25')
        self.assertEqual(Medicion.objects.count(), 1)
