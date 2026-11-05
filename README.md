# Cuentas de la casa

Para no olvidar la luz, el agua, el arriendo y el resto. `mysite` es la configuración. `cuentas` es la aplicación.

El recorrido de servicios es el mismo que en `polls`: el índice lista los servicios, el detalle muestra un formulario y el POST marca la cuenta elegida como pagada.

En la tabla `Cuenta` también hay formularios para crear, ver, editar y borrar.

## Cómo correrla

```bat
venv\Scripts\activate
python manage.py migrate
python manage.py runserver
```

Abre http://127.0.0.1:8000/

| Dirección | Qué muestra |
| --- | --- |
| `/` | Redirige a `/cuentas/` |
| `/cuentas/` | Lista de servicios |
| `/cuentas/1/` | Formulario para elegir una cuenta de ese servicio |
| `/cuentas/1/pagar/` | Recibe el POST y marca la cuenta elegida |
| `/cuentas/1/results/` | Cómo quedaron las cuentas de ese servicio |
| `/cuentas/lista/` | Todas las cuentas, con enlaces a ver, editar y borrar |
| `/cuentas/nueva/` | Formulario para crear una cuenta |
| `/cuentas/cuenta/5/` | El detalle de esa cuenta |
| `/cuentas/cuenta/5/editar/` | Formulario para modificarla |
| `/cuentas/cuenta/5/borrar/` | Formulario para eliminarla |
| `/cuentas/pagadas/` | Las que ya se pagaron |
| `/admin/` | Alta de servicios y cuentas |
