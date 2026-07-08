{\rtf1\ansi\ansicpg1252\cocoartf2870
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import os\
import requests\
from flask import Flask, request, jsonify\
\
app = Flask(__name__)\
\
# Configuraci\'f3n mediante variables de entorno (por seguridad)\
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")\
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")\
# Opcional: Define una clave secreta en Meraki y verif\'edcala aqu\'ed para mayor seguridad\
MERAKI_SECRET = os.environ.get("MERAKI_SECRET", "")\
\
def send_telegram_message(text):\
    url = f"https://api.telegram.org/bot\{TELEGRAM_TOKEN\}/sendMessage"\
    payload = \{\
        "chat_id": TELEGRAM_CHAT_ID,\
        "text": text,\
        "parse_mode": "Markdown" # Permite usar negritas y formato limpio\
    \}\
    try:\
        response = requests.post(url, json=payload)\
        return response.status_code == 200\
    except Exception as e:\
        print(f"Error enviando a Telegram: \{e\}")\
        return False\
\
@app.route('/webhook', methods=['POST'])\
def webhook_receiver():\
    # Validar entrada JSON\
    if not request.is_json:\
        return jsonify(\{"error": "Invalid JSON"\}), 400\
    \
    data = request.json\
\
    # (Opcional) Validar el shared secret si lo configuraste en Meraki\
    if MERAKI_SECRET and request.headers.get('X-Meraki-Secret') != MERAKI_SECRET:\
        return jsonify(\{"error": "Unauthorized"\}), 401\
\
    # Extraer datos clave de la alerta de Meraki\
    network_name = data.get("networkName", "Red Desconocida")\
    alert_type = data.get("alertType", "Alerta General")\
    occurred_at = data.get("occurredAt", "Tiempo no especificado")\
    device_name = data.get("deviceName", "N/A")\
    \
    # Formatear el mensaje para Telegram\
    message = (\
        f"\uc0\u55357 \u57000  *Nueva Alerta de Meraki* \u55357 \u57000 \\n\\n"\
        f"\uc0\u55356 \u57104  *Red:* \{network_name\}\\n"\
        f"\uc0\u9888 \u65039  *Tipo:* \{alert_type\}\\n"\
        f"\uc0\u55357 \u56524  *Dispositivo:* \{device_name\}\\n"\
        f"\uc0\u55357 \u56517  *Hora:* \{occurred_at\}\\n\\n"\
        f"\uc0\u55357 \u56541  *Detalles:* \{data.get('alertData', \{\})\}"\
    )\
\
    # Enviar a Telegram\
    if send_telegram_message(message):\
        return jsonify(\{"status": "success"\}), 200\
    else:\
        return jsonify(\{"status": "failed to send telegram notification"\}), 500\
\
if __name__ == '__main__':\
    # Meraki requiere HTTPS, las plataformas Cloud usualmente manejan el SSL por nosotros\
    port = int(os.environ.get("PORT", 5000))\
    app.run(host='0.0.0.0', port=port)}