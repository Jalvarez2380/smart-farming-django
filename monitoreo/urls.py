from django.urls import path

from . import views

app_name = 'monitoreo'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('parcelas/', views.parcelas, name='parcelas'),
    path('sensores/', views.sensores, name='sensores'),
    path('mediciones/registrar/', views.registrar_medicion, name='registrar'),
    path('historico/', views.historico, name='historico'),
]
