from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import redirect, render

from .forms import FiltroMedicionesForm, MedicionForm
from .models import Medicion, Parcela, Sensor


def dashboard(request):
    return render(request, 'monitoreo/dashboard.html', {
        'total_parcelas': Parcela.objects.count(),
        'total_sensores': Sensor.objects.count(),
        'total_mediciones': Medicion.objects.count(),
        'mediciones': Medicion.objects.select_related('sensor__parcela')[:8],
    })


def parcelas(request):
    return render(request, 'monitoreo/parcelas.html', {'parcelas': Parcela.objects.all()})


def sensores(request):
    return render(request, 'monitoreo/sensores.html', {
        'sensores': Sensor.objects.select_related('parcela'),
    })


def registrar_medicion(request):
    form = MedicionForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Medición registrada correctamente.')
        return redirect('monitoreo:historico')
    return render(request, 'monitoreo/registrar.html', {
        'form': form, 'umbral_humedad_baja': settings.UMBRAL_HUMEDAD_BAJA,
    })


def historico(request):
    form = FiltroMedicionesForm(request.GET)
    mediciones = Medicion.objects.select_related('sensor__parcela')
    if form.is_valid():
        if form.cleaned_data['parcela']:
            mediciones = mediciones.filter(sensor__parcela=form.cleaned_data['parcela'])
        if form.cleaned_data['tipo']:
            mediciones = mediciones.filter(sensor__tipo=form.cleaned_data['tipo'])
    else:
        mediciones = mediciones.none()
    page = Paginator(mediciones, 20).get_page(request.GET.get('page'))
    params = request.GET.copy()
    params.pop('page', None)
    return render(request, 'monitoreo/historico.html', {
        'form': form, 'mediciones': page, 'page_obj': page, 'filtros': params.urlencode(),
    })
