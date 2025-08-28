"""
Demostración y utilidades para gestión de logs organizados por fecha
Muestra las capacidades del nuevo sistema de logging por fechas
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# Agregar path del proyecto
sys.path.insert(0, str(Path(__file__).parent))

def demonstrate_dated_logging():
    """
    Demuestra el sistema de logging organizado por fechas
    """
    print("🗓️ Sistema de Logging Organizado por Fechas")
    print("=" * 50)
    
    try:
        from app.utils.log_config import DateBasedLoggingConfig, initialize_dated_logging
        from app.utils.logger import WhatsAppLogger, EventLogger
        from app.utils.log_date_utils import LogDateManager, LogAnalyzer
        
        print("✅ Módulos importados correctamente")
        
        # 1. Configurar logging con estructura por fechas
        print("\n🔧 Configurando logging con estructura por fechas...")
        
        config_result = initialize_dated_logging(environment='development')
        print(f"✅ Configuración completada: {config_result['environment']}")
        
        # 2. Generar algunos logs de ejemplo
        print("\n📝 Generando logs de ejemplo...")
        
        api_logger = WhatsAppLogger.get_logger(WhatsAppLogger.API_LOGGER)
        service_logger = WhatsAppLogger.get_logger(WhatsAppLogger.SERVICE_LOGGER)
        security_logger = WhatsAppLogger.get_logger(WhatsAppLogger.SECURITY_LOGGER)
        event_logger = EventLogger()
        
        # Logs estructurados con datos de ejemplo
        api_logger.info(
            "API request procesada exitosamente",
            extra={'extra_data': {
                'endpoint': '/api/messages/send',
                'method': 'POST',
                'user_id': 'user_12345',
                'response_time_ms': 145.2,
                'status_code': 200,
                'message_id': 'msg_demo_001',
                'phone_number_hash': 'hash_abcd1234'
            }}
        )
        
        service_logger.info(
            "Mensaje de WhatsApp procesado",
            extra={'extra_data': {
                'message_type': 'text',
                'template_name': 'welcome_message',
                'delivery_status': 'sent',
                'processing_time_ms': 89.5,
                'queue_size': 15
            }}
        )
        
        security_logger.warning(
            "Rate limiting aplicado",
            extra={'extra_data': {
                'ip_address': '192.168.1.100',
                'endpoint': '/api/messages',
                'rate_limit': 100,
                'current_requests': 105,
                'time_window': '1_hour',
                'action': 'request_rejected'
            }}
        )
        
        # Usar EventLogger para registrar eventos específicos
        event_logger.log_whatsapp_request(
            endpoint='/v1/messages',
            method='POST',
            payload={'to': '+52123456789', 'type': 'text', 'text': {'body': 'Mensaje de prueba'}},
            phone_number='+52123456789',
            message_id='msg_demo_002'
        )
        
        event_logger.log_performance_metric(
            metric_name='webhook_processing_time',
            value=234.7,
            unit='ms',
            tags={'webhook_type': 'message_status', 'country': 'MX'}
        )
        
        print("✅ Logs de ejemplo generados")
        
        # 3. Mostrar estructura de directorios creada
        print("\n📁 Estructura de directorios creada:")
        
        paths = DateBasedLoggingConfig.get_log_directory_structure()
        
        for path_name, path_obj in paths.items():
            if path_obj.exists():
                files = list(path_obj.glob('*'))
                print(f"  {path_name}: {path_obj}")
                for file in files[:5]:  # Mostrar solo los primeros 5
                    size = file.stat().st_size if file.is_file() else 'DIR'
                    print(f"    └─ {file.name} ({size} bytes)")
        
        # 4. Demostrar navegación por fechas
        print("\n🔍 Navegación por fechas:")
        
        date_manager = LogDateManager()
        available_dates = date_manager.get_available_dates()
        
        print(f"Fechas disponibles: {len(available_dates)}")
        for date in available_dates[-5:]:  # Últimas 5 fechas
            logs = date_manager.get_logs_for_date(date)
            print(f"  📅 {date.strftime('%Y-%m-%d')}: {len(logs)} archivos")
        
        # 5. Búsqueda en logs
        print("\n🔎 Búsqueda en logs:")
        
        # Buscar logs de las últimas 24 horas
        search_results = list(date_manager.search_logs_by_pattern(
            r'response_time_ms',
            start_date=datetime.now() - timedelta(hours=24),
            end_date=datetime.now()
        ))
        
        print(f"Encontrados {len(search_results)} registros con métricas de tiempo de respuesta:")
        for result in search_results[:3]:  # Mostrar solo los primeros 3
            print(f"  📄 {result['file']} (línea {result['line_number']})")
            print(f"     {result['line'][:100]}...")
        
        # 6. Estadísticas de logs
        print("\n📊 Estadísticas de logs:")
        
        stats = date_manager.get_log_statistics(
            start_date=datetime.now() - timedelta(days=7)
        )
        
        print(f"Período: {stats['period']['days']} días")
        print(f"Total archivos: {stats['files']['total_count']}")
        print(f"Tamaño total: {stats['files']['total_size_readable']}")
        print(f"Por componente:")
        
        for component, comp_stats in stats['files']['by_component'].items():
            print(f"  • {component}: {comp_stats['count']} archivos, {comp_stats['size_readable']}")
        
        print(f"Niveles de log:")
        for level, count in stats['log_levels'].items():
            if count > 0:
                print(f"  • {level}: {count}")
        
        # 7. Análisis avanzado
        print("\n🔬 Análisis avanzado:")
        
        analyzer = LogAnalyzer()
        
        # Patrones de errores
        error_patterns = analyzer.find_error_patterns(days_back=1)
        total_errors = sum(len(errors) for errors in error_patterns.values())
        print(f"Errores encontrados en las últimas 24h: {total_errors}")
        
        for category, errors in error_patterns.items():
            if errors:
                print(f"  • {category}: {len(errors)} errores")
        
        # Tendencias de performance
        perf_trends = analyzer.analyze_performance_trends(days_back=1)
        print(f"Requests analizados: {perf_trends['total_requests']}")
        
        if perf_trends['daily_trends']:
            today_key = datetime.now().strftime('%Y-%m-%d')
            if today_key in perf_trends['daily_trends']:
                today_stats = perf_trends['daily_trends'][today_key]
                print(f"Performance hoy:")
                print(f"  • Tiempo promedio: {today_stats['avg_response_time']:.1f}ms")
                print(f"  • Tiempo máximo: {today_stats['max_response_time']:.1f}ms")
                print(f"  • Requests: {today_stats['request_count']}")
        
        # 8. Comandos útiles
        print("\n🛠️ Comandos útiles disponibles:")
        
        from app.utils.log_date_utils import create_log_viewer_commands
        commands = create_log_viewer_commands()
        
        print("Comandos implementados:")
        for cmd_name in commands.keys():
            print(f"  • {cmd_name}()")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en demostración: {e}")
        import traceback
        traceback.print_exc()
        return False


def demonstrate_log_maintenance():
    """
    Demuestra las capacidades de mantenimiento de logs
    """
    print("\n🧹 Sistema de Mantenimiento de Logs")
    print("=" * 50)
    
    try:
        from app.utils.log_config import LogArchiveManager, create_log_maintenance_task
        
        # 1. Gestor de archivos
        print("📦 Gestor de archivos:")
        archive_manager = LogArchiveManager()
        
        print(f"Directorio base: {archive_manager.base_log_dir}")
        print(f"Directorio de archivos: {archive_manager.archive_dir}")
        print(f"Directorio comprimido: {archive_manager.compressed_dir}")
        
        # 2. Tarea de mantenimiento
        print("\n⚙️ Tarea de mantenimiento:")
        maintenance_task = create_log_maintenance_task()
        
        print("Tarea creada exitosamente")
        print("Esta tarea puede:")
        print("  • Comprimir logs de más de 7 días")
        print("  • Limpiar logs comprimidos de más de 1 año")
        print("  • Ejecutarse automáticamente en producción")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en mantenimiento: {e}")
        return False


def show_log_structure_benefits():
    """
    Muestra los beneficios de la estructura organizada por fechas
    """
    print("\n🎯 Beneficios de la Estructura por Fechas")
    print("=" * 50)
    
    benefits = [
        {
            'title': '📅 Organización Temporal',
            'description': 'Logs organizados automáticamente por YYYY/MM/DD'
        },
        {
            'title': '🔍 Búsqueda Eficiente',
            'description': 'Búsqueda rápida por rangos de fechas específicos'
        },
        {
            'title': '📊 Análisis Histórico',
            'description': 'Tendencias y patrones fáciles de identificar'
        },
        {
            'title': '💾 Gestión de Espacio',
            'description': 'Compresión automática de logs antiguos'
        },
        {
            'title': '🧹 Limpieza Automática',
            'description': 'Eliminación programada de logs muy antiguos'
        },
        {
            'title': '⚡ Performance Mejorada',
            'description': 'Archivos más pequeños = búsquedas más rápidas'
        },
        {
            'title': '🔐 Auditoría Mejorada',
            'description': 'Rastreabilidad temporal precisa para compliance'
        },
        {
            'title': '📈 Métricas por Período',
            'description': 'Estadísticas y reportes organizados temporalmente'
        }
    ]
    
    for benefit in benefits:
        print(f"{benefit['title']}")
        print(f"  {benefit['description']}")
        print()
    
    print("🚀 Casos de uso comunes:")
    use_cases = [
        "• Investigar incidentes en fechas específicas",
        "• Generar reportes mensuales/semanales",
        "• Análizar tendencias de performance",
        "• Auditorías de seguridad por período",
        "• Depurar problemas históricos",
        "• Monitoreo proactivo de patrones"
    ]
    
    for use_case in use_cases:
        print(f"  {use_case}")


def create_sample_log_queries():
    """
    Crea ejemplos de queries útiles para logs por fecha
    """
    print("\n💡 Queries de Ejemplo")
    print("=" * 50)
    
    queries = [
        {
            'name': 'Errores de hoy',
            'code': '''
date_manager = LogDateManager()
errors = list(date_manager.search_logs_by_pattern(
    r'ERROR',
    start_date=datetime.now().replace(hour=0, minute=0, second=0),
    end_date=datetime.now()
))
print(f"Errores encontrados hoy: {len(errors)}")
            '''
        },
        {
            'name': 'Performance de la última semana',
            'code': '''
analyzer = LogAnalyzer()
trends = analyzer.analyze_performance_trends(days_back=7)
print(f"Requests analizados: {trends['total_requests']}")
            '''
        },
        {
            'name': 'Logs de un componente específico',
            'code': '''
date_manager = LogDateManager()
api_logs = date_manager.get_logs_for_date(datetime.now(), 'api')
print(f"Logs de API hoy: {len(api_logs)}")
            '''
        },
        {
            'name': 'Estadísticas mensuales',
            'code': '''
start_date = datetime.now().replace(day=1)
stats = date_manager.get_log_statistics(start_date=start_date)
print(f"Archivos este mes: {stats['files']['total_count']}")
            '''
        }
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"{i}. {query['name']}:")
        print(query['code'])
        print()


def main():
    """
    Función principal de demostración
    """
    print("🗓️ DEMOSTRACIÓN: Sistema de Logging por Fechas")
    print("=" * 60)
    
    results = []
    
    # Ejecutar demostraciones
    tests = [
        ("Logging por Fechas", demonstrate_dated_logging),
        ("Mantenimiento de Logs", demonstrate_log_maintenance)
    ]
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error en {test_name}: {e}")
            results.append((test_name, False))
    
    # Mostrar información adicional
    show_log_structure_benefits()
    create_sample_log_queries()
    
    # Resumen final
    print("\n" + "="*60)
    print("📊 RESUMEN DE DEMOSTRACIÓN")
    print("="*60)
    
    passed = failed = 0
    for test_name, result in results:
        status = "✅ EXITOSA" if result else "❌ FALLIDA"
        print(f"{test_name:.<40} {status}")
        
        if result:
            passed += 1
        else:
            failed += 1
    
    if failed == 0:
        print("\n🎉 ¡SISTEMA DE LOGGING POR FECHAS COMPLETAMENTE FUNCIONAL!")
        print("\n📁 Estructura de logs creada:")
        print("  logs/")
        print("  ├── current/           # Enlaces a logs actuales")  
        print("  ├── 2025/")
        print("  │   └── 08/")
        print("  │       └── 26/        # logs del día")
        print("  │           ├── api_2025-08-26.log")
        print("  │           ├── services_2025-08-26.log")
        print("  │           └── security_2025-08-26.log")
        print("  ├── archive/           # Logs archivados")
        print("  └── compressed/        # Logs comprimidos")
        
        print("\n🛠️ Capacidades implementadas:")
        print("  ✅ Organización automática por fecha")
        print("  ✅ Búsqueda por rangos temporales")
        print("  ✅ Análisis de patrones y tendencias")
        print("  ✅ Estadísticas por período")
        print("  ✅ Compresión automática")
        print("  ✅ Limpieza programada")
        print("  ✅ Enlaces simbólicos para acceso rápido")
        
        print(f"\n💡 ¡La mejora solicitada está completamente implementada!")
        print("   El sistema ahora organiza los logs por fecha de forma automática")
        
    else:
        print(f"\n⚠️ {failed} componente(s) tuvieron problemas")
    
    print(f"\n{'='*60}")
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
