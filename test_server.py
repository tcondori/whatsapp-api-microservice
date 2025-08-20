"""
Script simple para probar la aplicación Flask
"""
from entrypoint import app

if __name__ == '__main__':
    print("🔧 Iniciando servidor de prueba...")
    print("📚 Health check disponible en: http://127.0.0.1:5000/health")
    print("📖 Documentación en: http://127.0.0.1:5000/docs/")
    
    # Ejecutar con configuración específica
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True,
        use_reloader=False  # Evitar que se reinicie automáticamente
    )
