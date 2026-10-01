from django.contrib import admin

from .models import Medicion, Parcela, Sensor


@admin.register(Parcela)
class ParcelaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'ubicacion']
    search_fields = ['nombre', 'ubicacion']


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'tipo', 'parcela', 'unidad', 'estado']
    list_filter = ['tipo', 'estado', 'parcela']
    search_fields = ['codigo', 'parcela__nombre']
    list_select_related = ['parcela']


@admin.register(Medicion)
class MedicionAdmin(admin.ModelAdmin):
    list_display = ['sensor', 'valor', 'fecha_hora', 'alerta_humedad']
    list_filter = ['sensor__tipo', 'sensor__parcela', 'fecha_hora']
    search_fields = ['sensor__codigo', 'sensor__parcela__nombre']
    list_select_related = ['sensor']
    readonly_fields = ['fecha_hora']

    @admin.display(boolean=True, description='Humedad baja')
    def alerta_humedad(self, obj):
        return obj.humedad_baja
