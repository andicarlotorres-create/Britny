# 🎲 Bot de Dados para Telegram - Render.com

Bot simple de juego de dados desplegado en Render.com

## 🚀 Despliegue Rápido

1. **Crea estos archivos** en tu repositorio:
   - `bot.py` (código principal)
   - `requirements.txt` (dependencias)
   - `render.yaml` (configuración de Render)
   - `runtime.txt` (versión Python)

2. **Ve a [render.com](https://render.com)**
3. **Haz clic en "New +" → "Web Service"**
4. **Conecta tu repositorio de GitHub**
5. **Configura:**
   - Name: `telegram-dice-bot`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python bot.py`
   - Plan: `Free`

6. **Haz clic en "Create Web Service"**

## 📱 Comandos del Bot

1. `/start` - Inicia el bot
2. `/play` - Juega una partida
3. `/stats` - Ver tus estadísticas
4. `/ranking` - Ver top 10
5. `/rules` - Reglas del juego
6. `/help` - Ayuda

## 🌐 URLs del Servicio

- Web: `https://telegram-dice-bot.onrender.com`
- Health: `https://telegram-dice-bot.onrender.com/health`
- Ping: `https://telegram-dice-bot.onrender.com/ping`

## ⚠️ Notas Importantes

1. **Token expuesto**: Cambia el token en `bot.py` línea 10
2. **Free tier**: Se duerme tras 15 minutos inactivo
3. **Auto-reactivación**: Se activa automáticamente al recibir mensajes
4. **Estadísticas**: Se guardan en memoria (se pierden al reiniciar)

## 🔧 Para Mantener Activo

Agrega un ping automático cada 5 minutos:
- Usa [UptimeRobot.com](https://uptimerobot.com)
- URL: `https://tu-bot.onrender.com/ping`
- Intervalo: 5 minutos

---

**¡Listo! Tu bot está funcionando 24/7 en la nube.** 🎉
