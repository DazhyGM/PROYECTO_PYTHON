from datetime import datetime

from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views import generic

from .models import Cuenta, Servicio


class IndexView(generic.ListView):
    template_name = "cuentas/index.html"
    context_object_name = "servicio_list"

    def get_queryset(self):
        return Servicio.objects.order_by("nombre")


class DetailView(generic.DetailView):
    model = Servicio
    template_name = "cuentas/detail.html"


class ResultsView(generic.DetailView):
    model = Servicio
    template_name = "cuentas/results.html"


class PagadasView(generic.ListView):
    template_name = "cuentas/pagadas.html"
    context_object_name = "cuentas"

    def get_queryset(self):
        return Cuenta.objects.filter(pagada=True).order_by("-vence")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total"] = context["cuentas"].aggregate(Sum("valor"))["valor__sum"] or 0
        return context


class CuentaListView(generic.ListView):
    template_name = "cuentas/lista.html"
    context_object_name = "cuenta_list"

    def get_queryset(self):
        return Cuenta.objects.order_by("servicio__nombre", "mes")


class CuentaDetailView(generic.DetailView):
    model = Cuenta
    template_name = "cuentas/ver.html"


def pagar(request, servicio_id):
    servicio = get_object_or_404(Servicio, pk=servicio_id)
    try:
        cuenta_elegida = servicio.cuenta_set.get(pk=request.POST["cuenta"])
    except (KeyError, Cuenta.DoesNotExist):
        return render(
            request,
            "cuentas/detail.html",
            {
                "servicio": servicio,
                "error_message": "No seleccionaste una cuenta.",
            },
        )
    else:
        cuenta_elegida.pagada = True
        cuenta_elegida.save()
        return HttpResponseRedirect(reverse("cuentas:results", args=(servicio.id,)))


def datos_del_formulario(post):
    try:
        servicio = Servicio.objects.get(pk=post["servicio"])
        mes = post["mes"].strip()
        valor = int(post["valor"])
        vence = datetime.strptime(post["vence"], "%Y-%m-%d")
        vence = timezone.make_aware(vence)
        if mes == "":
            raise ValueError
    except (KeyError, Servicio.DoesNotExist, ValueError):
        return None
    return {
        "servicio": servicio,
        "mes": mes,
        "valor": valor,
        "vence": vence,
        "pagada": "pagada" in post,
    }


def contexto_formulario(post, cuenta=None):
    if post is not None:
        servicio_id = post.get("servicio")
        mes = post.get("mes", "")
        valor = post.get("valor", "")
        vence = post.get("vence", "")
        pagada = "pagada" in post
    else:
        servicio_id = cuenta.servicio_id
        mes = cuenta.mes
        valor = cuenta.valor
        vence = timezone.localtime(cuenta.vence).strftime("%Y-%m-%d")
        pagada = cuenta.pagada
    try:
        servicio_id = int(servicio_id)
    except (TypeError, ValueError):
        servicio_id = None
    return {
        "servicio_list": Servicio.objects.order_by("nombre"),
        "servicio_id": servicio_id,
        "mes": mes,
        "valor": valor,
        "vence": vence,
        "pagada": pagada,
        "cuenta": cuenta,
    }


def crear(request):
    if request.method == "POST":
        datos = datos_del_formulario(request.POST)
        if datos is None:
            context = contexto_formulario(request.POST)
            context["error_message"] = "Revisa el servicio, el mes, el valor y la fecha (AAAA-MM-DD)."
            return render(request, "cuentas/crear.html", context)
        cuenta = Cuenta.objects.create(**datos)
        return HttpResponseRedirect(reverse("cuentas:ver", args=(cuenta.id,)))
    return render(
        request,
        "cuentas/crear.html",
        {
            "servicio_list": Servicio.objects.order_by("nombre"),
            "mes": "",
            "valor": "",
            "vence": "",
            "pagada": False,
        },
    )


def editar(request, cuenta_id):
    cuenta = get_object_or_404(Cuenta, pk=cuenta_id)
    if request.method == "POST":
        datos = datos_del_formulario(request.POST)
        if datos is None:
            context = contexto_formulario(request.POST, cuenta)
            context["error_message"] = "Revisa el servicio, el mes, el valor y la fecha (AAAA-MM-DD)."
            return render(request, "cuentas/editar.html", context)
        cuenta.servicio = datos["servicio"]
        cuenta.mes = datos["mes"]
        cuenta.valor = datos["valor"]
        cuenta.vence = datos["vence"]
        cuenta.pagada = datos["pagada"]
        cuenta.save()
        return HttpResponseRedirect(reverse("cuentas:ver", args=(cuenta.id,)))
    return render(request, "cuentas/editar.html", contexto_formulario(None, cuenta))


def borrar(request, cuenta_id):
    cuenta = get_object_or_404(Cuenta, pk=cuenta_id)
    if request.method == "POST":
        cuenta.delete()
        return HttpResponseRedirect(reverse("cuentas:lista"))
    return render(request, "cuentas/borrar.html", {"cuenta": cuenta})
