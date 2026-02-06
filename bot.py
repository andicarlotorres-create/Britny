import os
import random
import logging
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ===== CONFIGURACIÓN =====
BOT_TOKEN = "8519041982:AAG9y3iaC9S9nk2bOo5rkI1-OMcXgsavG2o"
ADMIN_ID = 6667062973
PORT = int(os.environ.get('PORT', 10000))

# ===== LOGGING =====
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===== DATOS =====
players_db = {}

# ===== FLASK PARA RENDER =====
app = Flask(__name__)

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🎲 Bot de Dados Telegram</title>
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
            h1 {
                font-size: 2.5em;
                margin-bottom: 20px;
            }
            .status {
                font-size: 1.2em;
                background: rgba(0, 255, 0, 0.2);
                padding: 10px;
                border-radius: 10px;
                margin: 20px 0;
            }
            .command {
                background: rgba(255, 255, 255, 0.2);
                padding: 10px;
                margin: 10px;
                border-radius: 8px;
                display: inline-block;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎲 Bot de Dados Telegram</h1>
            <div class="status">✅ Bot en línea y funcionando</div>
            <p>Este bot está alojado en Render.com y funciona 24/7</p>
            <div>
                <strong>Comandos disponibles:</strong><br>
                <span class="command">/start</span>
                <span class="command">/play</span>
                <span class="command">/stats</span>
                <span class="command">/ranking</span>
                <span class="command">/rules</span>
            </div>
            <p style="margin-top: 30px;">
                👉 Busca <strong>@DiceGameMasterBot</strong> en Telegram<br>
                📊 Jugadores registrados: """ + str(len(players_db)) + """
            </p>
        </div>
    </body>
    </html>
    """

@app.route('/health')
def health():
    return "OK", 200

@app.route('/ping')
def ping():
    return "pong", 200

# ===== COMANDOS DEL BOT =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("🎯 JUGAR AHORA", callback_data="play_now")],
        [InlineKeyboardButton("📊 VER ESTADÍSTICAS", callback_data="view_stats")],
        [InlineKeyboardButton("🏆 RANKING GLOBAL", callback_data="view_ranking")]
    ]
    await update.message.reply_text(
        f"🎲 *¡BIENVENIDO {user.first_name.upper()}!*\n\n"
        "Soy tu bot de dados personal 🤖\n"
        "Presiona *JUGAR AHORA* para empezar o usa:\n"
        "• /play - Para jugar\n"
        "• /stats - Tus estadísticas\n"
        "• /ranking - Top 10\n"
        "• /rules - Reglas del juego\n\n"
        "¡Buena suerte! 🍀",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    if user_id not in players_db:
        players_db[user_id] = {
            'name': user.first_name,
            'wins': 0,
            'losses': 0,
            'draws': 0,
            'total': 0,
            'score': 0
        }
    
    keyboard = [
        [InlineKeyboardButton("🎲 TIRAR DADO", callback_data="roll_dice")],
        [InlineKeyboardButton("📈 MIS ESTADÍSTICAS", callback_data="my_stats")]
    ]
    
    await update.message.reply_text(
        f"🎯 *{user.first_name}, ¿LISTO PARA JUGAR?*\n\n"
        "Presiona *TIRAR DADO* para lanzar tu dado.\n"
        "El bot tirará automáticamente el suyo.\n"
        "¡GANA EL NÚMERO MÁS ALTO!",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    if user_id in players_db:
        stats = players_db[user_id]
        win_rate = (stats['wins'] / stats['total'] * 100) if stats['total'] > 0 else 0
        
        await update.message.reply_text(
            f"📊 *ESTADÍSTICAS DE {user.first_name.upper()}*\n\n"
            f"🏆 Victorias: {stats['wins']}\n"
            f"😢 Derrotas: {stats['losses']}\n"
            f"🤝 Empates: {stats['draws']}\n"
            f"🎯 Total: {stats['total']} juegos\n"
            f"⭐ Puntuación: {stats['score']} puntos\n"
            f"📈 Porcentaje: {win_rate:.1f}% de victorias\n\n"
            f"¡Sigue jugando para mejorar!",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "📊 *Aún no tienes estadísticas*\n\n"
            "¡Usa /play para jugar tu primera partida! 🎲",
            parse_mode='Markdown'
        )

async def ranking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not players_db:
        await update.message.reply_text(
            "🏆 *RANKING VACÍO*\n\n"
            "¡Sé el primero en jugar! Usa /play 🎲",
            parse_mode='Markdown'
        )
        return
    
    sorted_players = sorted(
        players_db.items(),
        key=lambda x: x[1]['score'],
        reverse=True
    )[:10]
    
    text = "🏆 *TOP 10 JUGADORES* 🏆\n\n"
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    
    for idx, (user_id, stats) in enumerate(sorted_players):
        if idx < len(medals):
            text += f"{medals[idx]} *{stats['name']}*\n"
            text += f"   ⭐ {stats['score']} pts | 🏆 {stats['wins']}\n\n"
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📜 *REGLAS DEL JUEGO DE DADOS*\n\n"
        "1. 🎯 *Cada jugador tira un dado* (números 1-6)\n"
        "2. 🤖 *El bot tira su dado* automáticamente\n"
        "3. 🏆 *Gana el número más alto*\n"
        "4. ⚖️ *Empate si son iguales*\n\n"
        "📊 *SISTEMA DE PUNTOS:*\n"
        "✅ Victoria = +3 puntos\n"
        "🤝 Empate = +1 punto\n"
        "❌ Derrota = +0 puntos\n\n"
        "¡Usa /play para empezar! 🚀",
        parse_mode='Markdown'
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🆘 *AYUDA - COMANDOS DISPONIBLES*\n\n"
        "🎮 *PARA JUGAR:*\n"
        "/start - Inicia el bot\n"
        "/play - Juega una partida\n\n"
        "📊 *INFORMACIÓN:*\n"
        "/stats - Tus estadísticas\n"
        "/ranking - Top 10 jugadores\n"
        "/rules - Reglas del juego\n"
        "/help - Muestra esta ayuda\n\n"
        "⚡ *EL BOT ESTÁ 24/7 EN LA NUBE*\n"
        "✅ Siempre disponible\n"
        "📈 Estadísticas en tiempo real\n"
        "🏆 Ranking actualizado\n\n"
        "¡Diviértete! 😄",
        parse_mode='Markdown'
    )

# ===== MANEJADOR DE BOTONES =====
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    user_id = user.id
    data = query.data
    
    if data == "play_now" or data == "roll_dice":
        # Asegurar que el usuario está en la base de datos
        if user_id not in players_db:
            players_db[user_id] = {
                'name': user.first_name,
                'wins': 0,
                'losses': 0,
                'draws': 0,
                'total': 0,
                'score': 0
            }
        
        # Tirar dados
        user_dice = random.randint(1, 6)
        bot_dice = random.randint(1, 6)
        
        # Determinar resultado
        if user_dice > bot_dice:
            result = "🎉 *¡HAS GANADO!* 🎉"
            points = 3
            players_db[user_id]['wins'] += 1
        elif user_dice < bot_dice:
            result = "😢 *Has perdido...*"
            points = 0
            players_db[user_id]['losses'] += 1
        else:
            result = "🤝 *¡EMPATE!*"
            points = 1
            players_db[user_id]['draws'] += 1
        
        # Actualizar estadísticas
        players_db[user_id]['total'] += 1
        players_db[user_id]['score'] += points
        
        # Crear mensaje
        dice_emojis = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]
        message = (
            f"🎲 *RESULTADO DE LA PARTIDA*\n\n"
            f"👤 **{user.first_name}**: {dice_emojis[user_dice-1]} *{user_dice}*\n"
            f"🤖 **Bot**: {dice_emojis[bot_dice-1]} *{bot_dice}*\n\n"
            f"{result}\n"
            f"⭐ Puntos ganados: *{points}*\n"
            f"📊 Puntuación total: *{players_db[user_id]['score']}*\n\n"
            f"¿Jugamos otra? 🎯"
        )
        
        keyboard = [
            [InlineKeyboardButton("🎲 TIRAR DE NUEVO", callback_data="roll_dice")],
            [
                InlineKeyboardButton("📊 MIS ESTADÍSTICAS", callback_data="my_stats"),
                InlineKeyboardButton("🏆 RANKING", callback_data="view_ranking")
            ],
            [InlineKeyboardButton("📜 REGLAS", callback_data="view_rules")]
        ]
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif data == "view_stats" or data == "my_stats":
        if user_id in players_db:
            stats = players_db[user_id]
            win_rate = (stats['wins'] / stats['total'] * 100) if stats['total'] > 0 else 0
            
            message = (
                f"📊 *ESTADÍSTICAS PERSONALES*\n\n"
                f"👤 Jugador: *{user.first_name}*\n"
                f"🏆 Victorias: *{stats['wins']}*\n"
                f"😢 Derrotas: *{stats['losses']}*\n"
                f"🤝 Empates: *{stats['draws']}*\n"
                f"🎯 Total juegos: *{stats['total']}*\n"
                f"⭐ Puntuación: *{stats['score']}*\n"
                f"📈 % Victorias: *{win_rate:.1f}%*\n\n"
                f"¡Sigue así! 💪"
            )
        else:
            message = "📊 *Aún no has jugado*\n\n¡Presiona 🎲 para empezar!"
        
        keyboard = [
            [InlineKeyboardButton("🎲 JUGAR AHORA", callback_data="roll_dice")],
            [InlineKeyboardButton("🏆 VER RANKING", callback_data="view_ranking")],
            [InlineKeyboardButton("🔙 VOLVER", callback_data="back_menu")]
        ]
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif data == "view_ranking":
        if not players_db:
            message = "🏆 *RANKING VACÍO*\n\n¡Sé el primero en jugar! 🎲"
        else:
            sorted_players = sorted(
                players_db.items(),
                key=lambda x: x[1]['score'],
                reverse=True
            )[:5]
            
            message = "🏆 *TOP 5 JUGADORES* 🏆\n\n"
            medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
            
            for idx, (uid, stats) in enumerate(sorted_players):
                if idx < 5:
                    message += f"{medals[idx]} *{stats['name']}*\n"
                    message += f"   ⭐ {stats['score']} pts | 🏆 {stats['wins']}\n\n"
        
        keyboard = [
            [InlineKeyboardButton("🎲 JUGAR YO", callback_data="roll_dice")],
            [InlineKeyboardButton("📊 MIS ESTADÍSTICAS", callback_data="my_stats")],
            [InlineKeyboardButton("🔙 VOLVER", callback_data="back_menu")]
        ]
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif data == "view_rules":
        message = (
            "📜 *REGLAS RÁPIDAS*\n\n"
            "1. 🎯 Tiras un dado (1-6)\n"
            "2. 🤖 Bot tira su dado\n"
            "3. 🏆 Gana número más alto\n"
            "4. ⚖️ Empate si iguales\n\n"
            "🏅 *PUNTUACIÓN:*\n"
            "✅ Ganar = +3 puntos\n"
            "🤝 Empate = +1 punto\n"
            "❌ Perder = 0 puntos"
        )
        
        keyboard = [
            [InlineKeyboardButton("🎲 ¡QUIERO JUGAR!", callback_data="roll_dice")],
            [InlineKeyboardButton("🔙 VOLVER", callback_data="back_menu")]
        ]
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif data == "back_menu":
        keyboard = [
            [InlineKeyboardButton("🎯 JUGAR AHORA", callback_data="play_now")],
            [InlineKeyboardButton("📊 VER ESTADÍSTICAS", callback_data="view_stats")],
            [InlineKeyboardButton("🏆 RANKING GLOBAL", callback_data="view_ranking")]
        ]
        
        await query.edit_message_text(
            f"🎲 *MENÚ PRINCIPAL*\n\n"
            f"¡Hola {user.first_name}! 👋\n"
            f"Elige una opción para continuar:",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# ===== FUNCIÓN PARA INICIAR FLASK =====
def run_flask():
    app.run(host='0.0.0.0', port=PORT)

# ===== FUNCIÓN PRINCIPAL =====
def main():
    logger.info("🚀 INICIANDO BOT PARA RENDER.COM")
    logger.info(f"📱 Token: {BOT_TOKEN[:10]}...")
    logger.info(f"👑 Admin ID: {ADMIN_ID}")
    logger.info(f"🌐 Puerto: {PORT}")
    
    # Iniciar Flask en segundo plano
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Crear aplicación de Telegram
    app_tg = Application.builder().token(BOT_TOKEN).build()
    
    # Añadir comandos
    app_tg.add_handler(CommandHandler("start", start))
    app_tg.add_handler(CommandHandler("play", play))
    app_tg.add_handler(CommandHandler("stats", stats))
    app_tg.add_handler(CommandHandler("ranking", ranking))
    app_tg.add_handler(CommandHandler("rules", rules))
    app_tg.add_handler(CommandHandler("help", help_cmd))
    
    # Añadir manejador de botones
    app_tg.add_handler(CallbackQueryHandler(button_handler))
    
    # Iniciar bot
    logger.info("✅ Bot listo. Iniciando polling...")
    print("\n" + "="*50)
    print("🎲 BOT DE DADOS TELEGRAM - RENDER.COM")
    print("="*50)
    print(f"🌐 Web: http://0.0.0.0:{PORT}")
    print(f"❤️  Health: http://0.0.0.0:{PORT}/health")
    print("📱 Busca tu bot en Telegram y usa /start")
    print("="*50 + "\n")
    
    app_tg.run_polling()

if __name__ == "__main__":
    main()
