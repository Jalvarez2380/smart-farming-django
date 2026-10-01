from django.test import Client
from django.urls import reverse

from monitoreo.models import Medicion

from .base import DatosMonitoreo


class PruebaAceptacion(DatosMonitoreo):
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
