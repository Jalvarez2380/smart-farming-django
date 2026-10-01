from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from monitoreo.models import Medicion, Parcela, Sensor


class Command(BaseCommand):
    help = 'Carga dos parcelas, seis sensores y doce mediciones sin duplicar los ejemplos.'

    @transaction.atomic
    def handle(self, *args, **options):
        ejemplos = [
            (Sensor.Tipo.HUMEDAD, '%', ['24.50', '48.00']),
            (Sensor.Tipo.TEMPERATURA, '°C', ['26.20', '27.80']),
            (Sensor.Tipo.RADIACION, 'W/m²', ['420.00', '560.00']),
        ]
        for numero, cultivo in enumerate(['Cacao', 'Maíz'], start=1):
            parcela, _ = Parcela.objects.get_or_create(
                nombre=f'Demo · {cultivo}', ubicacion=f'Puyo, sector demostrativo {numero}',
                defaults={'descripcion': f'Parcela académica de {cultivo.lower()}.'},
            )
            for tipo, unidad, valores in ejemplos:
                sensor, _ = Sensor.objects.get_or_create(
                    codigo=f'DEMO-{numero}-{tipo}',
                    defaults={'parcela': parcela, 'tipo': tipo, 'unidad': unidad},
                )
                for valor in valores:
                    Medicion.objects.get_or_create(sensor=sensor, valor=Decimal(valor))
        self.stdout.write(self.style.SUCCESS('Datos demo disponibles; los existentes se conservan.'))
