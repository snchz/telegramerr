## Solución de Problemas Frecuentes

**Error: `TelegramConflictError: terminated by other getUpdates request`**
Telegram tiene una regla estricta: un Token de bot solo puede estar conectado a **un único programa a la vez**. Si estás reutilizando un token que ya usas en otro sitio (como notificaciones de Radarr o Home Assistant), ambos programas "pelearán" por leer los mensajes y Telegram bloqueará la conexión.
👉 **Solución**: Ve a `@BotFather` en Telegram, crea un bot completamente nuevo (`/newbot`) y usa ese nuevo token exclusivamente para Telegramerr.
