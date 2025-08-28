#!/usr/bin/env python
"""
Paso 1: Instalación de PostgreSQL con Docker
Opción más fácil y rápida para desarrollo
"""

def docker_installation():
    """
    Guía completa para instalar PostgreSQL con Docker
    """
    print("=== 🐳 PASO 1A: POSTGRESQL CON DOCKER ===\n")
    
    print("VENTAJAS DE DOCKER:")
    print("✅ Instalación en 5 minutos")
    print("✅ No afecta el sistema principal")
    print("✅ Fácil de eliminar si hay problemas")
    print("✅ Configuración consistente")
    print("✅ Ideal para desarrollo")
    
    print(f"\n1. VERIFICAR DOCKER")
    print("-" * 30)
    print("Comando: docker --version")
    print("Si no tienes Docker:")
    print("• Descargar de: https://www.docker.com/products/docker-desktop")
    print("• Instalar Docker Desktop para Windows")
    
    print(f"\n2. COMANDO DE INSTALACIÓN")
    print("-" * 30)
    print("Copiar y ejecutar este comando:")
    print()
    
    docker_command = """docker run --name postgres-whatsapp \\
  -e POSTGRES_DB=whatsapp_chatbot \\
  -e POSTGRES_USER=whatsapp_user \\
  -e POSTGRES_PASSWORD=whatsapp_2024 \\
  -p 5432:5432 \\
  -v postgres_data:/var/lib/postgresql/data \\
  -d postgres:15-alpine"""
    
    print(docker_command)
    
    print(f"\n3. VERIFICAR INSTALACIÓN")
    print("-" * 30)
    print("# Ver que el contenedor esté corriendo:")
    print("docker ps")
    print()
    print("# Ver logs si hay problemas:")
    print("docker logs postgres-whatsapp")
    
    print(f"\n4. DATOS DE CONEXIÓN")
    print("-" * 30)
    print("Host: localhost")
    print("Puerto: 5432")
    print("Base de datos: whatsapp_chatbot")
    print("Usuario: whatsapp_user")
    print("Password: whatsapp_2024")
    
    print(f"\n5. COMANDOS ÚTILES")
    print("-" * 30)
    print("# Conectar desde línea de comandos:")
    print("docker exec -it postgres-whatsapp psql -U whatsapp_user -d whatsapp_chatbot")
    print()
    print("# Detener/iniciar:")
    print("docker stop postgres-whatsapp")
    print("docker start postgres-whatsapp")
    print()
    print("# Si quieres empezar de cero:")
    print("docker rm -f postgres-whatsapp")
    print("docker volume rm postgres_data")

def native_installation():
    """
    Guía para instalación nativa en Windows
    """
    print(f"\n=== 💻 PASO 1B: POSTGRESQL NATIVO (ALTERNATIVA) ===\n")
    
    print("VENTAJAS INSTALACIÓN NATIVA:")
    print("✅ Mejor rendimiento")
    print("✅ Herramientas GUI incluidas (pgAdmin)")
    print("✅ Ideal para producción")
    print("✅ Servicios Windows automáticos")
    
    print(f"\n1. DESCARGAR POSTGRESQL")
    print("-" * 30)
    print("• Ir a: https://www.postgresql.org/download/windows/")
    print("• Descargar PostgreSQL 15 o 16 (versión estable)")
    print("• Ejecutar el instalador .exe")
    
    print(f"\n2. CONFIGURACIÓN DURANTE INSTALACIÓN")
    print("-" * 30)
    print("• Puerto: 5432 (dejar por defecto)")
    print("• Superuser password: whatsapp_2024 (o la que prefieras)")
    print("• Instalar pgAdmin 4: ✅ SÍ")
    print("• Instalar Stack Builder: ✅ SÍ")
    
    print(f"\n3. POST-INSTALACIÓN")
    print("-" * 30)
    print("• Abrir pgAdmin 4")
    print("• Crear nueva base de datos: 'whatsapp_chatbot'")
    print("• Crear usuario: 'whatsapp_user' con password 'whatsapp_2024'")
    print("• Dar permisos al usuario sobre la base de datos")

def recommendation():
    """
    Recomendación final
    """
    print(f"\n=== 🎯 RECOMENDACIÓN ===\n")
    
    print("PARA DESARROLLO (Recomendado): 🐳 Docker")
    print("• Más rápido de instalar")
    print("• Menos problemas de configuración")
    print("• Fácil de limpiar si algo sale mal")
    
    print(f"\nPARA PRODUCCIÓN FUTURA: 💻 Instalación Nativa")
    print("• Mejor rendimiento")
    print("• Herramientas de administración completas")
    
    print(f"\n📋 SIGUIENTE PASO:")
    print("1. Elige una opción (Docker recomendada)")
    print("2. Ejecuta la instalación")
    print("3. Confirma que PostgreSQL está corriendo")
    print("4. ¡Avísame cuando esté listo para continuar con el Paso 2!")

if __name__ == "__main__":
    docker_installation()
    native_installation()
    recommendation()
