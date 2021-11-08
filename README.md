# ACMVoting-bot
## Comandos del bot

- */start* - Inicia la conversación con el bot (como es lógico)
- */candidaturas* - Muestra al usuario las candidaturas a votar
- */registrarme* - Introduce al usuario (id, alias, nombre) en la BD de votantes
  registrados.
- */votar* - Permite al usuario votar a la candidatura que quiera (voto secreto,
  al solo marcar en la BD si el usuario ha votado, pero no a quién)

## Dependencias

Solo depende del paquete `python-telegram-bot`, que se instala por medio de
**pip**.

Obviamente, Python 3.

## Desplegar el bot
### Docker

Si se despliega desde Docker (la forma más sencilla), solo se necesitan correr
dos comandos.

Crear la imagen de Docker:
```
docker build --tag acmvoting_bot .
```

Y desplegar la imagen:
```
docker run --detach --name acmvoting_bot acmvoting_bot:latest
```

Y ya está, para poder acceder a él (si fuese necesario tocar), solo hay que
abrir un Shell dentro:
```
docker exec -it acmvoting_bot sh
```

## Local

Si en cambio se quiere correr desde local, lo primero es instalar las
dependencias, y luego, ejecutar el siguiente comando:
```
python acmvoting-bot/acmvoting-bot.py &
```

El `&` es para que corra por detrás de la terminal.

Si lo queremos desacoplar de la terminal (poder cerrarla y que el bot siga),
usamos el comando `jobs` para ver el número asignado, y corremos el siguiente
comando, cambiando la N por el número de job asignado):
```
disown %N
```
