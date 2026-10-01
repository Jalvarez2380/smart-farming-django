from django import forms

from .models import Medicion, Parcela, Sensor


class MedicionForm(forms.ModelForm):
    class Meta:
        model = Medicion
        fields = ['sensor', 'valor']
        widgets = {'valor': forms.NumberInput(attrs={'step': '0.01'})}
        help_texts = {'valor': 'Use la unidad indicada en el sensor. Humedad: entre 0 y 100 %.'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sensor'].queryset = Sensor.objects.filter(estado=Sensor.Estado.ACTIVO)
        self.fields['sensor'].empty_label = 'Seleccione un sensor activo'


class FiltroMedicionesForm(forms.Form):
    parcela = forms.ModelChoiceField(queryset=Parcela.objects.all(), required=False,
                                    empty_label='Todas las parcelas')
    tipo = forms.ChoiceField(choices=[('', 'Todos los tipos'), *Sensor.Tipo.choices], required=False)
