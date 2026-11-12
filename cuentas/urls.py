from django.urls import path

from . import views

app_name = "cuentas"

urlpatterns = [
    path("", views.inicio, name="index"),
    path("servicios/", views.ServiciosView.as_view(), name="servicios"),
    path("entrar/", views.entrar, name="entrar"),
    path("registro/", views.registro, name="registro"),
    path("salir/", views.salir, name="salir"),
    path("perfil/", views.perfil, name="perfil"),
    path("usuarios/", views.panel, name="usuarios"),
    path("pagadas/", views.PagadasView.as_view(), name="pagadas"),
    path("lista/", views.CuentaListView.as_view(), name="lista"),
    path("nueva/", views.crear, name="crear"),
    path("cuenta/<int:pk>/", views.CuentaDetailView.as_view(), name="ver"),
    path("cuenta/<int:cuenta_id>/editar/", views.editar, name="editar"),
    path("cuenta/<int:cuenta_id>/pagar/", views.marcar, name="marcar"),
    path("cuenta/<int:cuenta_id>/borrar/", views.borrar, name="borrar"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path("<int:pk>/results/", views.ResultsView.as_view(), name="results"),
    path("<int:servicio_id>/pagar/", views.pagar, name="pagar"),
]
