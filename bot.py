import os
import random
import logging
import requests
import threading
import time
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ===== CONFIGURACIÓN =====
BOT_TOKEN = "8519041982:AAG9y3iaC9S9nk2bOo5rkI1-OMcXgsavG2o"
ADMIN_ID = 6667062973
PORT = int(os.environ.get('PORT', 10000))
RENDER_URL = "https://telegram-dice-bot.onrender.com"  # Cambia con tu URL

# ===== LOGGING MEJORADO =====
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===== DATOS =====
players_db = {}

# ===== FLASK MEJORADO =====
app = Flask(__name__)

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🎲 Bot de Dados - SIEMPRE ACTIVO</title>
        <meta http-equiv="refresh" content="300">
        <style>
            body {
                font-family: Arial, sans-serif;
                text-align: center;
                padding: 50px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container {
                background: rgba(255, 255, 255, 0.1);
                padding: 30px;
                border-radius: 15px;
                backdrop-filter: blur(10px);
                max-width: 600px;
                margin: 0 auto;
            }
            .status {
                font-size: 1.2em;
                background: rgba(0, 255, 0, 0.3);
                padding: 15px;
                border-radius: 10px;
                margin: 20px 0;
            }
            .info {
                background: rgba(255, 255, 255, 0.1);
                padding: 15px;
                border-radius: 10px;
                margin: 15px 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎲 Bot de Dados Telegram</h1>
            <div class="status">✅ INSTANCIA ACTIVA - SIEMPRE EN LÍNEA</div>
            
            <div class="info">
                <h3>📊 Estado del Servidor</h3>
                <p>🔄 Auto-ping cada 5 minutos</p>
                <p>📈 Jugadores registrados: """ + str(len(players_db)) + """</p>
                <p>⚡ Respuesta instantánea en Telegram</p>
            </div>
            
            <div class="info">
                <h3>🔗 Enlaces Útiles</h3>
                <p><a href="/health" style="color: #4CAF50;">/health</a> - Verificar estado</p>
                <p><a href="/stats" style="color: #2196F3;">/stats</a> - Estadísticas del bot</p>
                <p><a href="/ping" style="color: #FF9800;">/ping</a> - Mantener activo</p>
            </div>
            
            <div class="info">
                <h3>📱 Usa el Bot</h3>
                <p>Busca <strong>@DiceGameMasterBot</strong> en Telegram</p>
                <p>Comandos: /start, /play, /stats, /ranking</p>
            </div>
            
            <p style="margin-top: 30px; font-size: 0.9em; opacity: 0.8;">
                Último ping: <span id="lastPing">""" + time.strftime("%H:%M:%S") + """</span>
            </p>
        </div>
        
        <script>
            // Actualizar hora del último ping
            function updateTime() {
                const now = new Date();
                document.getElementById('lastPing').textContent = 
                    now.getHours().toString().padStart(2, '0') + ':' +
                    now.getMinutes().toString().padStart(2, '0') + ':' +
                    now.getSeconds().toString().padStart(2, '0');
            }
            setInterval(updateTime, 1000);
            
            // Ping automático cada 4 minutos
            setInterval(() => {
                fetch('/ping').then(() => {
                    updateTime();
                    console.log('✅ Ping automático enviado');
                });
            }, 240000);
        </script>
    </body>
    </html>
    """

@app.route('/health')
def health():
    return {
        "status": "active",
        "service": "telegram-dice-bot",
        "players": len(players_db),
        "timestamp": time.time(),
        "message": "✅ Bot funcionando correctamente"
    }, 200

@app.route('/stats')
def stats_page():
    return {
        "total_players": len(players_db),
        "total_games": sum(p['total'] for p in players_db.values()),
        "active": True,
        "uptime": time.time() - start_time if 'start_time' in globals() else 0
    }, 200

@app.route('/ping')
def ping():
    return "pong", 200

# ===== KEEP-ALIVE AUTOMÁTICO =====
def keep_alive_ping():
    """Envía pings automáticos para mantener la instancia activa"""
    time.sleep(30)  # Esperar a que todo inicie
    
    while True:
        try:
            # Ping a sí mismo
            response = requests.get(f"{RENDER_URL}/ping", timeout=10)
            logger.info(f"🔄 Ping automático: {response.status_code}")
            
            # También ping a health
            requests.get(f"{RENDER_URL}/health", timeout=10)
            
        except Exception as e:
            logger.warning(f"⚠️ Error en ping automático: {e}")
        
        # Esperar 4 minutos (Render duerme después de 5-15 minutos)
        time.sleep(240)

# ===== FUNCIONES DEL BOT (IGUALES QUE ANTES) =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"🎲 *¡HOLA {user.first_name}!*\n\n"
        "Soy tu bot de dados 🤖\n"
        "✅ *INSTANCIA ACTIVA 24/7*\n\n"
        "Usa /play para jugar o elige:\n"
        "• /stats - Tus estadísticas\n"
        "• /ranking - Top 10\n"
        "• /rules - Reglas\n"
        "• /help - Ayuda\n\n"
        "¡Responde al instante! ⚡",
        parse_mode='Markdown'
    )

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    if user_id not in players_db:
        players_db[user_id] = {
            'name': user.first_name,
            'wins': 0, 'losses': 0, 'draws': 0,
            'total': 0, 'score': 0
        }
    
    # Tirar dados
    user_dice = random.randint(1, 6)
    bot_dice = random.randint(1, 6)
    
    # Determinar resultado
    if user_dice > bot_dice:
        result = "🎉 *¡GANASTE!*"
        points = 3
        players_db[user_id]['wins'] += 1
    elif user_dice < bot_dice:
        result = "😢 *Perdiste...*"
        points = 0
        players_db[user_id]['losses'] += 1
    else:
        result = "🤝 *¡EMPATE!*"
        points = 1
        players_db[user_id]['draws'] += 1
    
    players_db[user_id]['total'] += 1
    players_db[user_id]['score'] += points
    
    await update.message.reply_text(
        f"🎲 *RESULTADO*\n\n"
        f"🎯 Tú: *{user_dice}*\n"
        f"🤖 Bot: *{bot_dice}*\n\n"
        f"{result}\n"
        f"⭐ +{points} puntos\n"
        f"📊 Total: {players_db[user_id]['score']} pts\n\n"
        f"Usa /play para otra partida!",
        parse_mode='Markdown'
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    if user_id in players_db:
        stats = players_db[user_id]
        win_rate = (stats['wins'] / stats['total'] * 100) if stats['total'] > 0 else 0
        
        await update.message.reply_text(
            f"📊 *ESTADÍSTICAS*\n\n"
            f"👤 {user.first_name}\n"
            f"🏆 {stats['wins']} victorias\n"
            f"😢 {stats['losses']} derrotas\n"
            f"🤝 {stats['draws']} empates\n"
            f"🎯 {stats['total']} partidas\n"
            f"⭐ {stats['score']} puntos\n"
            f"📈 {win_rate:.1f}% de éxito",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "📊 *Aún no has jugado*\n¡Usa /play para empezar! 🎲",
            parse_mode='Markdown'
        )

async def ranking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not players_db:
        await update.message.reply_text("🏆 *No hay jugadores aún*")
        return
    
    sorted_players = sorted(players_db.items(), key=lambda x: x[1]['score'], reverse=True)[:10]
    
    text = "🏆 *TOP 10*\n\n"
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    
    for idx, (uid, stats) in enumerate(sorted_players):
        if idx < 10:
            text += f"{medals[idx]} {stats['name']}\n"
            text += f"   ⭐{stats['score']} pts | 🏆{stats['wins']}\n\n"
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📜 *REGLAS*\n\n"
        "1. 🎯 Tira dado (1-6)\n"
        "2. 🤖 Bot tira su dado\n"
        "3. 🏆 Gana número más alto\n"
        "4. ⚖️ Empate si iguales\n\n"
        "🏅 *PUNTOS:*\n✅ Ganar = +3\n🤝 Empate = +1\n❌ Perder = 0",
        parse_mode='Markdown'
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🆘 *AYUDA*\n\n"
        "🎮 /play - Jugar\n"
        "📊 /stats - Tus estadísticas\n"
        "🏆 /ranking - Top 10\n"
        "📜 /rules - Reglas\n"
        "🆘 /help - Esta ayuda\n\n"
        "⚡ *INSTANCIA SIEMPRE ACTIVA*",
        parse_mode='Markdown'
    )

# ===== INICIALIZACIÓN =====
start_time = time.time()

def main():
    logger.info("🚀 INICIANDO BOT CON KEEP-ALIVE")
    
    # Iniciar hilo de keep-alive
    ping_thread = threading.Thread(target=keep_alive_ping, daemon=True)
    ping_thread.start()
    
    # Crear app de Telegram
    app_tg = Application.builder().token(BOT_TOKEN).build()
    
    # Añadir handlers
    app_tg.add_handler(CommandHandler("start", start))
    app_tg.add_handler(CommandHandler("play", play))
    app_tg.add_handler(CommandHandler("stats", stats))
    app_tg.add_handler(CommandHandler("ranking", ranking))
    app_tg.add_handler(CommandHandler("rules", rules))
    app_tg.add_handler(CommandHandler("help", help_cmd))
    
    # Información
    print("\n" + "="*60)
    print("🎲 BOT DE DADOS - RENDER.COM")
    print("="*60)
    print(f"🌐 Web: https://telegram-dice-bot.onrender.com")
    print(f"❤️  Health: /health")
    print(f"🔄 Auto-ping: Cada 4 minutos")
    print(f"📊 Jugadores: {len(players_db)}")
    print("="*60)
    print("✅ Bot listo. Instancia siempre activa.")
    print("="*60 + "\n")
    
    # Iniciar bot
    app_tg.run_polling()

if __name__ == "__main__":
    main()