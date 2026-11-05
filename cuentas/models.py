from django.db import models


class Servicio(models.Model):
    nombre = models.CharField(max_length=200)

    def __str__(self):
        return self.nombre


class Cuenta(models.Model):
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    mes = models.CharField(max_length=200)
    valor = models.IntegerField(default=0)
    vence = models.DateTimeField("fecha de vencimiento")
    pagada = models.BooleanField(default=False)

    def __str__(self):
        return "%s %s" % (self.servicio, self.mes)
