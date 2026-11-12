from datetime import datetime

from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout,
    update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Prefetch, Q, Sum
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import generic
from django.views.decorators.http import require_POST

from .models import Cuenta, Rol, Servicio, Usuario

User = get_user_model()


def usuario_de(request):
    try:
        return request.user.usuario
    except Usuario.DoesNotExist:
        codigo = Rol.ADMINISTRADOR if request.user.is_staff or request.user.is_superuser else Rol.USUARIO
        perfil, _ = Usuario.objects.get_or_create(user=request.user, defaults={"rol": Rol.obtener(codigo)})
        return perfil


class ServiciosView(LoginRequiredMixin, generic.ListView):
    template_name = "cuentas/servicios.html"
    context_object_name = "servicio_list"

    def get_queryset(self):
        return Servicio.objects.order_by("nombre")


def cuentas_visibles(request, servicio=None):
    yo = usuario_de(request)
    if yo.es_administrador():
        consulta = Q(alcance=Cuenta.GRUPO) | Q(usuario=yo, alcance=Cuenta.PROPIA)
    else:
        consulta = Q(usuario=yo)
    origen = servicio.cuenta_set if servicio is not None else Cuenta.objects
    return origen.filter(consulta)


class DetailView(LoginRequiredMixin, generic.DetailView):
    model = Servicio
    template_name = "cuentas/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cuentas"] = cuentas_visibles(self.request, self.object)
        return context


class ResultsView(LoginRequiredMixin, generic.DetailView):
    model = Servicio
    template_name = "cuentas/results.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cuentas"] = cuentas_visibles(self.request, self.object)
        return context


class PagadasView(LoginRequiredMixin, generic.ListView):
    template_name = "cuentas/pagadas.html"
    context_object_name = "cuentas"

    def get_queryset(self):
        return Cuenta.objects.filter(usuario=usuario_de(self.request), pagada=True).order_by("-vence")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total"] = context["cuentas"].aggregate(Sum("valor"))["valor__sum"] or 0
        return context


class CuentaListView(LoginRequiredMixin, generic.ListView):
    template_name = "cuentas/lista.html"
    context_object_name = "cuenta_list"

    def get_queryset(self):
        return Cuenta.objects.filter(usuario=usuario_de(self.request)).order_by("servicio__nombre", "mes")


class CuentaDetailView(LoginRequiredMixin, generic.DetailView):
    model = Cuenta
    template_name = "cuentas/ver.html"

    def get_queryset(self):
        return Cuenta.objects.filter(usuario=usuario_de(self.request))


@login_required
def pagar(request, servicio_id):
    servicio = get_object_or_404(Servicio, pk=servicio_id)
    cuentas = cuentas_visibles(request, servicio)
    try:
        cuenta_elegida = cuentas.get(pk=request.POST["cuenta"])
    except (KeyError, Cuenta.DoesNotExist):
        return render(
            request,
            "cuentas/detail.html",
            {
                "servicio": servicio,
                "cuentas": cuentas,
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


@login_required
def crear(request):
    if request.method == "POST":
        datos = datos_del_formulario(request.POST)
        if datos is None:
            context = contexto_formulario(request.POST)
            context["error_message"] = "Revisa el servicio, el mes, el valor y la fecha (AAAA-MM-DD)."
            return render(request, "cuentas/crear.html", context)
        datos["usuario"] = usuario_de(request)
        datos["alcance"] = Cuenta.PROPIA
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


@login_required
def editar(request, cuenta_id):
    cuenta = get_object_or_404(Cuenta, pk=cuenta_id, usuario=usuario_de(request))
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
        cuenta.save()
        return HttpResponseRedirect(reverse("cuentas:ver", args=(cuenta.id,)))
    return render(request, "cuentas/editar.html", contexto_formulario(None, cuenta))


@login_required
@require_POST
def marcar(request, cuenta_id):
    cuenta = get_object_or_404(Cuenta, pk=cuenta_id, usuario=usuario_de(request))
    cuenta.pagada = True
    cuenta.save(update_fields=["pagada"])
    if request.POST.get("volver") == "ver":
        return HttpResponseRedirect(reverse("cuentas:ver", args=(cuenta.id,)))
    return HttpResponseRedirect(reverse("cuentas:lista"))


@login_required
def borrar(request, cuenta_id):
    cuenta = get_object_or_404(Cuenta, pk=cuenta_id, usuario=usuario_de(request))
    if request.method == "POST":
        cuenta.delete()
        return HttpResponseRedirect(reverse("cuentas:lista"))
    return render(request, "cuentas/borrar.html", {"cuenta": cuenta})


def destino_despues_de_entrar(request):
    siguiente = request.POST.get("next") or request.GET.get("next")
    if siguiente and url_has_allowed_host_and_scheme(
        siguiente,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return siguiente
    return reverse("cuentas:index")


def entrar(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("cuentas:index"))
    username = ""
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is None:
            return render(
                request,
                "cuentas/entrar.html",
                {
                    "username": username,
                    "next": request.POST.get("next", ""),
                    "error_message": "Usuario o contraseña incorrectos.",
                },
            )
        login(request, user)
        return HttpResponseRedirect(destino_despues_de_entrar(request))
    return render(
        request,
        "cuentas/entrar.html",
        {"username": username, "next": request.GET.get("next", "")},
    )


def registro(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("cuentas:index"))
    username = ""
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")
        error = None
        if username == "" or password == "":
            error = "Escribe el usuario y la contraseña."
        elif len(username) > 150:
            error = "El usuario no puede pasar de 150 caracteres."
        elif password != password2:
            error = "Las contraseñas no coinciden."
        elif User.objects.filter(username=username).exists():
            error = "Ese usuario ya existe."
        else:
            try:
                UnicodeUsernameValidator()(username)
                validate_password(password)
            except ValidationError as exc:
                error = " ".join(exc.messages)
            else:
                try:
                    user = User.objects.create_user(username=username, password=password)
                    Usuario.objects.get_or_create(user=user)
                except IntegrityError:
                    error = "Ese usuario ya existe."
                else:
                    login(request, user)
                    return HttpResponseRedirect(reverse("cuentas:index"))
        return render(
            request,
            "cuentas/registro.html",
            {"username": username, "error_message": error},
        )
    return render(request, "cuentas/registro.html", {"username": username})


@require_POST
def salir(request):
    logout(request)
    return HttpResponseRedirect(reverse("cuentas:entrar"))


@login_required
def perfil(request):
    perfil = usuario_de(request)
    usuario = perfil.user
    error = None
    actualizado = False
    if request.method == "POST":
        actual = request.POST.get("actual", "")
        password = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")
        if not usuario.check_password(actual):
            error = "La contraseña actual no coincide."
        elif password == "":
            error = "Escribe la contraseña nueva."
        elif password != password2:
            error = "Las contraseñas no coinciden."
        else:
            try:
                validate_password(password, usuario)
            except ValidationError as exc:
                error = " ".join(exc.messages)
            else:
                usuario.set_password(password)
                usuario.save()
                update_session_auth_hash(request, usuario)
                actualizado = True
    return render(
        request,
        "cuentas/perfil.html",
        {
            "perfil": perfil,
            "cuentas_propias": perfil.cuenta_set.filter(alcance=Cuenta.PROPIA).count(),
            "cuentas_grupo": perfil.cuenta_set.filter(alcance=Cuenta.GRUPO).count(),
            "error_message": error,
            "actualizado": actualizado,
        },
    )


def resumen(consulta):
    pagadas = consulta.filter(pagada=True).count()
    pendientes = consulta.filter(pagada=False).count()
    total = pagadas + pendientes
    porcentaje = f"{(pagadas * 100 / total):.1f}" if total else "0"
    return {
        "pagadas": pagadas,
        "pendientes": pendientes,
        "total": total,
        "porcentaje": porcentaje,
        "valor_pagadas": consulta.filter(pagada=True).aggregate(Sum("valor"))["valor__sum"] or 0,
        "valor_pendientes": consulta.filter(pagada=False).aggregate(Sum("valor"))["valor__sum"] or 0,
    }


def grupo_de_usuarios():
    cuentas = Cuenta.objects.filter(alcance=Cuenta.GRUPO).select_related("servicio").order_by("servicio__nombre", "mes")
    return (
        Usuario.objects.filter(rol__codigo=Rol.USUARIO)
        .select_related("user")
        .prefetch_related(Prefetch("cuenta_set", queryset=cuentas))
        .order_by("user__username")
    )


def resumen_del_grupo():
    return resumen(Cuenta.objects.filter(alcance=Cuenta.GRUPO))


@login_required
def panel(request):
    perfil = usuario_de(request)
    if not perfil.es_administrador():
        return render(request, "cuentas/sin_permiso.html", status=403)
    grupo = grupo_de_usuarios()
    error = None
    destino_id = None
    if request.method == "POST":
        datos = datos_del_formulario(request.POST)
        try:
            destino_id = int(request.POST.get("destino"))
        except (TypeError, ValueError):
            destino_id = None
        destino = Usuario.objects.filter(pk=destino_id, rol__codigo=Rol.USUARIO).first()
        if datos is None or destino is None:
            error = "Elige un usuario del grupo y revisa el servicio, el mes, el valor y la fecha (AAAA-MM-DD)."
            context = contexto_formulario(request.POST)
        else:
            datos["usuario"] = destino
            datos["alcance"] = Cuenta.GRUPO
            Cuenta.objects.create(**datos)
            return HttpResponseRedirect(reverse("cuentas:usuarios"))
    else:
        context = {
            "servicio_list": Servicio.objects.order_by("nombre"),
            "servicio_id": None,
            "mes": "",
            "valor": "",
            "vence": "",
            "pagada": False,
        }
    context.update(resumen_del_grupo())
    context["grupo"] = grupo
    context["destino_id"] = destino_id
    context["error_message"] = error
    return render(request, "cuentas/usuarios.html", context)


@login_required
def inicio(request):
    yo = usuario_de(request)
    if yo.es_administrador():
        del_grupo = Cuenta.objects.filter(alcance=Cuenta.GRUPO)
    else:
        del_grupo = Cuenta.objects.filter(usuario=yo, alcance=Cuenta.GRUPO)
    pendientes = (
        cuentas_visibles(request)
        .filter(pagada=False)
        .select_related("servicio")
        .order_by("vence")
    )
    return render(
        request,
        "cuentas/index.html",
        {
            "propias": resumen(Cuenta.objects.filter(usuario=yo, alcance=Cuenta.PROPIA)),
            "grupo": resumen(del_grupo),
            "ve_el_grupo": yo.es_administrador(),
            "pendientes": pendientes,
        },
    )
