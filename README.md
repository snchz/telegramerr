# Telegramerr

Un bot de Telegram ultraligero y rápido para buscar y solicitar películas y series directamente en tu servidor [Overseerr](https://overseerr.dev/). 

Creado para ser simple, seguro y perfecto para compartir con familiares y amigos a través de grupos de Telegram.

---

## ✨ Características Principales

- 🎬 **Búsqueda Dual**: Encuentra tanto películas como series de televisión con un solo comando.
- 📺 **Selección de Temporadas**: Si solicitas una serie, el bot te preguntará interactivamente qué temporada concreta quieres descargar (o todas).
- 🔔 **Notificaciones Automáticas**: El bot vigila tus descargas en segundo plano y te avisa en Telegram en cuanto la película o serie esté lista para ver.
- 🔒 **Seguridad por Whitelist**: Funciona mediante un mapeo estricto. Solo los usuarios (o grupos) que tú autorices explícitamente en la configuración podrán usar el bot.
- 📈 **Tendencias**: Descubre lo más popular de la semana con un simple comando.
- 🐳 **Optimizado para Docker**: Preparado para desplegarse en 1 minuto usando [Dockge](https://dockge.kuma.pet/) o Portainer.

---

## 🚀 Despliegue e Instalación

El método más fácil para instalar Telegramerr es usando Docker Compose (o [Dockge](https://dockge.kuma.pet/)).

1. Crea un nuevo stack/proyecto llamado `telegramerr`.
2. Copia el siguiente contenido en tu archivo `compose.yaml`:

```yaml
services:
  telegramerr:
    image: ghcr.io/snchz/telegramerr:latest
    container_name: telegramerr
    restart: unless-stopped
    environment:
      # Idioma principal del bot (es, en)
      - BOT_LANGUAGE=es
      # Tiempo en SEGUNDOS entre cada comprobación de notificaciones
      - POLLING_INTERVAL=60
      # Nivel de detalle de los logs (INFO, DEBUG, ERROR)
      - LOG_LEVEL=INFO
    env_file:
      - .env
```
*(Nota: Si has hecho un fork de este proyecto en GitHub, cambia `ghcr.io/snchz` por tu usuario).*

3. Crea un archivo `.env` en la misma carpeta y configúralo con tus datos:

```ini
# IMPORTANTE: El Token debe ser exclusivo para este bot.
TELEGRAM_BOT_TOKEN=tu_token_aqui_123456789
OVERSEERR_URL=http://tu_ip:5055
OVERSEERR_API_KEY=tu_api_key_de_overseerr

# Mapeo de seguridad: Relaciona IDs de Telegram con usuarios de Overseerr.
# USER_MAPPING={"ID_TELEGRAM": "ID_OVERSEERR"}
USER_MAPPING={"123456789": "1", "-1009876543": "1"}
```

4. ¡Pulsa **Deploy / Start** y el bot cobrará vida!

---

## 🔑 Cómo encontrar los IDs para la configuración

Para que la seguridad funcione, debes vincular quién pide en Telegram con quién lo pide en Overseerr en la variable `USER_MAPPING`.

- **ID de Telegram (`TU_ID_TELEGRAM`)**: 
  - Puede ser el ID de una **persona** o el ID de un **grupo** (para que cualquiera dentro del grupo pueda pedir).
  - ¿Cómo saberlo? Escribe `/start` a tu bot en Telegram. Si no estás autorizado, el propio bot te responderá con tu ID exacto (o el ID del grupo, que suele ser un número negativo como `-100123...`). ¡Cópialo!
- **ID de Overseerr (`TU_ID_OVERSEERR`)**:
  - Tiene que ser estrictamente el **ID numérico** de tu usuario en Overseerr (ej. `1`), NO tu nombre o correo.
  - ¿Cómo saberlo? Entra a Overseerr, ve a la sección *Users*, haz clic en el usuario deseado y fíjate en la barra de direcciones de tu navegador: `http://IP:5055/users/1`. El número final es el ID.

---

## ⚙️ Configurar los Comandos en Telegram (Autocompletar)

Para que Telegram te muestre un menú bonito y autocompletable al escribir la barra diagonal (`/`), debes registrar los comandos oficiales de tu bot usando `@BotFather`:

1. Abre un chat en Telegram con `@BotFather`.
2. Envíale el comando `/setcommands`.
3. Selecciona tu bot (ej. `@telegramerr_bot`).
4. Copia y pégale **exactamente** este bloque de texto:

```text
search - Buscar una pelicula o serie
trending - Ver lo mas popular de la semana
start - Iniciar el bot y ver estado
help - Ver la ayuda y comandos
```

*(Cuando te diga "Success!", tu bot ya estará perfectamente integrado. En los grupos, al poner `/search Matrix` el bot sabrá que le hablas a él sin tener que añadir el `@nombre` al final).*

---

## 📱 Guía de Uso

Una vez configurado y autorizado, interactuar con el bot es facilísimo:

- **`/search [título]`**: Busca cualquier película o serie. Ejemplo: `/search Iron Man`. El bot te responderá con la carátula, resumen, botones de paginación para ver otros resultados, y el botón verde para "Solicitar".
- **`/trending`**: Si no sabes qué ver, este comando te mostrará las películas y series que son tendencia esta semana.
- **Soporte de Grupos**: Si autorizas el ID de un grupo, cualquier miembro del grupo podrá invocar estos comandos y los avisos de "¡Tu petición ya está lista para ver!" llegarán directamente al grupo.

---

## 🛠️ Solución de Problemas Frecuentes

**Error: `TelegramConflictError: terminated by other getUpdates request`**  
Telegram tiene una regla estricta: **un Token de bot solo puede estar conectado a un único programa a la vez**. Si estás reutilizando un token que ya usas en otro sitio (por ejemplo, en Radarr o en Home Assistant), ambos programas "pelearán" por leer los mensajes y Telegram bloqueará la conexión del bot.  
👉 **Solución**: Ve a `@BotFather` en Telegram, crea un bot completamente nuevo (`/newbot`) y usa ese nuevo token *exclusivamente* para Telegramerr.

---

## 🔄 Actualizaciones Automáticas

Este repositorio utiliza **GitHub Actions**. Al hacer un *push* a la rama `main`, la imagen de Docker se compilará y publicará automáticamente en `ghcr.io`. Para actualizar tu bot a la última versión, simplemente ve a tu gestor (Dockge/Portainer) y haz clic en **Update** o recompila la imagen.
