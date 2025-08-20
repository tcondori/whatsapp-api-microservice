"""
Endpoint temporal de debug para verificar configuración
"""
from flask import Flask, jsonify, current_app
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

@app.route('/debug-config')
def debug_config():
    """Endpoint para debug de configuración"""
    return jsonify({
        'env_vars': {
            'FLASK_ENV': os.getenv('FLASK_ENV'),
            'DEBUG': os.getenv('DEBUG'),
            'WEBHOOK_VERIFY_TOKEN': os.getenv('WEBHOOK_VERIFY_TOKEN'),
            'VALID_API_KEYS': os.getenv('VALID_API_KEYS'),
            'WHATSAPP_ACCESS_TOKEN': 'SET' if os.getenv('WHATSAPP_ACCESS_TOKEN') else 'NOT SET'
        },
        'flask_config': {
            'DEBUG': current_app.config.get('DEBUG'),
            'FLASK_ENV': current_app.config.get('FLASK_ENV'),
            'WEBHOOK_VERIFY_TOKEN': current_app.config.get('WEBHOOK_VERIFY_TOKEN'),
            'VALID_API_KEYS': current_app.config.get('VALID_API_KEYS'),
            'WHATSAPP_ACCESS_TOKEN': 'SET' if current_app.config.get('WHATSAPP_ACCESS_TOKEN') else 'NOT SET'
        }
    })

if __name__ == '__main__':
    from config import get_config
    config = get_config()
    app.config.from_object(config)
    app.run(host='127.0.0.1', port=5001, debug=True)
