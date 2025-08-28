"""
Configuraciones de logging específicas por entorno
Manejo de configuraciones para desarrollo, testing y producción con organización por fechas
"""

import os
import logging.config
import gzip
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any


class DateBasedLoggingConfig:
    """
    Configuraciones de logging por entorno con organización por fechas
    """
    
    @staticmethod
    def get_log_directory_structure(base_log_dir: str = 'logs') -> Dict[str, Path]:
        """
        Crea estructura de directorios organizados por fecha
        
        Returns:
            Dict con paths para diferentes períodos
        """
        base_path = Path(base_log_dir)
        today = datetime.now()
        
        # Estructura: logs/YYYY/MM/DD/
        current_date_path = base_path / str(today.year) / f"{today.month:02d}" / f"{today.day:02d}"
        
        # Crear estructura de directorios
        current_date_path.mkdir(parents=True, exist_ok=True)
        
        # También crear directorio para logs actuales (enlace directo)
        current_path = base_path / 'current'
        current_path.mkdir(exist_ok=True)
        
        return {
            'base': base_path,
            'current_date': current_date_path,
            'current': current_path,
            'archive': base_path / 'archive',
            'compressed': base_path / 'compressed'
        }
    
    @staticmethod
    def get_dated_log_filename(component: str, date: datetime = None) -> str:
        """
        Genera nombre de archivo de log con fecha
        
        Args:
            component: Nombre del componente (api, webhook, service, etc.)
            date: Fecha para el log (default: hoy)
            
        Returns:
            Nombre de archivo con fecha
        """
        if date is None:
            date = datetime.now()
        
        date_str = date.strftime('%Y-%m-%d')
        return f"{component}_{date_str}.log"
    
    @staticmethod
    def get_base_config_with_dates() -> Dict[str, Any]:
        """
        Configuración base común con soporte para fechas
        """
        return {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    'datefmt': '%Y-%m-%d %H:%M:%S'
                },
                'detailed': {
                    'format': '%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s:%(lineno)d - %(message)s',
                    'datefmt': '%Y-%m-%d %H:%M:%S'
                },
                'json_dated': {
                    '()': 'app.utils.logger.JsonFormatter',
                    'include_extra': True
                },
                'json_simple_dated': {
                    '()': 'app.utils.logger.JsonFormatter', 
                    'include_extra': False
                }
            },
            'filters': {},
            'handlers': {},
            'loggers': {},
            'root': {
                'level': 'INFO',
                'handlers': []
            }
        }
    
    @staticmethod
    def get_development_config_with_dates(dual_output: bool = True) -> Dict[str, Any]:
        """
        Configuración para desarrollo con estructura por fechas y dual output
        """
        config = DateBasedLoggingConfig.get_base_config_with_dates()
        
        # Crear estructura de directorios
        paths = DateBasedLoggingConfig.get_log_directory_structure()
        
        # Agregar formatters para dual output
        if dual_output:
            config['formatters']['simple_terminal'] = {
                '()': 'app.utils.logger.SimpleTextFormatter'
            }
            try:
                import colorlog
                config['formatters']['color_terminal'] = {
                    'class': 'colorlog.ColoredFormatter',
                    'format': '%(log_color)s[%(asctime)s] %(levelname)-8s%(reset)s - %(message)s',
                    'datefmt': '%H:%M:%S',
                    'log_colors': {
                        'DEBUG': 'cyan',
                        'INFO': 'green', 
                        'WARNING': 'yellow',
                        'ERROR': 'red',
                        'CRITICAL': 'red,bg_white',
                    }
                }
                terminal_formatter = 'color_terminal'
            except ImportError:
                terminal_formatter = 'simple_terminal'
        
        # Nombres de archivo con fecha
        today = datetime.now()
        
        handlers = {
            'file_api_dated': {
                'class': 'app.utils.log_config.DatedRotatingFileHandler',
                'level': 'DEBUG',
                'formatter': 'json_dated',
                'base_filename': str(paths['current'] / 'api.log'),
                'dated_filename': str(paths['current_date'] / DateBasedLoggingConfig.get_dated_log_filename('api')),
                'maxBytes': 10485760,  # 10MB
                'backupCount': 3,
                'encoding': 'utf8'
            },
            'file_service_dated': {
                'class': 'app.utils.log_config.DatedRotatingFileHandler',
                'level': 'DEBUG',
                'formatter': 'json_dated',
                'base_filename': str(paths['current'] / 'services.log'),
                'dated_filename': str(paths['current_date'] / DateBasedLoggingConfig.get_dated_log_filename('services')),
                'maxBytes': 10485760,
                'backupCount': 3,
                'encoding': 'utf8'
            },
            'file_webhook_dated': {
                'class': 'app.utils.log_config.DatedRotatingFileHandler',
                'level': 'DEBUG',
                'formatter': 'json_dated',
                'base_filename': str(paths['current'] / 'webhooks.log'),
                'dated_filename': str(paths['current_date'] / DateBasedLoggingConfig.get_dated_log_filename('webhooks')),
                'maxBytes': 10485760,
                'backupCount': 3,
                'encoding': 'utf8'
            },
            'file_security_dated': {
                'class': 'app.utils.log_config.DatedRotatingFileHandler',
                'level': 'WARNING',
                'formatter': 'json_dated',
                'base_filename': str(paths['current'] / 'security.log'),
                'dated_filename': str(paths['current_date'] / DateBasedLoggingConfig.get_dated_log_filename('security')),
                'maxBytes': 10485760,
                'backupCount': 7,  # Mantener más días para seguridad
                'encoding': 'utf8'
            },
            'file_database_dated': {
                'class': 'app.utils.log_config.DatedRotatingFileHandler',
                'level': 'DEBUG',
                'formatter': 'json_dated',
                'base_filename': str(paths['current'] / 'database.log'),
                'dated_filename': str(paths['current_date'] / DateBasedLoggingConfig.get_dated_log_filename('database')),
                'maxBytes': 10485760,
                'backupCount': 3,
                'encoding': 'utf8'
            },
            'file_performance_dated': {
                'class': 'app.utils.log_config.DatedRotatingFileHandler',
                'level': 'DEBUG',
                'formatter': 'json_dated',
                'base_filename': str(paths['current'] / 'performance.log'),
                'dated_filename': str(paths['current_date'] / DateBasedLoggingConfig.get_dated_log_filename('performance')),
                'maxBytes': 10485760,
                'backupCount': 3,
                'encoding': 'utf8'
            }
        }
        
        # Agregar handler de terminal si dual_output está habilitado
        if dual_output:
            handlers['console'] = {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
                'formatter': terminal_formatter,
                'stream': 'ext://sys.stdout'
            }
        
        config['handlers'] = handlers
        
        # Configurar loggers con handlers duales si está habilitado
        logger_handlers = ['file_api_dated']
        if dual_output:
            logger_handlers.append('console')
            
        config['loggers'] = {
            'whatsapp_api': {
                'level': 'DEBUG',
                'handlers': logger_handlers,
                'propagate': False
            },
            'whatsapp_webhook': {
                'level': 'DEBUG', 
                'handlers': ['file_webhook_dated'] + (['console'] if dual_output else []),
                'propagate': False
            },
            'whatsapp_service': {
                'level': 'DEBUG',
                'handlers': ['file_service_dated'] + (['console'] if dual_output else []),
                'propagate': False
            },
            'whatsapp_database': {
                'level': 'DEBUG',
                'handlers': ['file_database_dated'] + (['console'] if dual_output else []),
                'propagate': False
            },
            'whatsapp_performance': {
                'level': 'DEBUG',
                'handlers': ['file_performance_dated'] + (['console'] if dual_output else []),
                'propagate': False
            },
            'whatsapp_security': {
                'level': 'WARNING',
                'handlers': ['file_security_dated'] + (['console'] if dual_output else []),
                'propagate': False
            }
        }
        
        config['root'] = {
            'level': 'INFO',
            'handlers': ['console'] if dual_output else []
        }
        
        return config
    
    @staticmethod
    def get_production_config_with_dates(dual_output: bool = False) -> Dict[str, Any]:
        """
        Configuración para producción con estructura por fechas avanzada
        """
        config = DateBasedLoggingConfig.get_base_config_with_dates()
        
        # Directorio de logs en producción
        log_base = Path('/var/log/whatsapp-api') if os.name == 'posix' else Path('logs')
        
        # Crear estructura de directorios para producción
        paths = DateBasedLoggingConfig.get_log_directory_structure(str(log_base))
        
        config['handlers'] = {
            'console_error': {
                'class': 'logging.StreamHandler',
                'level': 'ERROR',
                'formatter': 'json_simple_dated',
                'stream': 'ext://sys.stderr'
            },
            'file_app_dated': {
                'class': 'app.utils.log_config.DatedTimedRotatingFileHandler',
                'level': 'INFO',
                'formatter': 'json_dated',
                'base_filename': str(paths['current'] / 'app.log'),
                'dated_path': str(paths['current_date']),
                'when': 'midnight',
                'interval': 1,
                'backupCount': 30,
                'encoding': 'utf8',
                'compress_after_days': 7
            },
            'file_security_dated': {
                'class': 'app.utils.log_config.DatedTimedRotatingFileHandler',
                'level': 'WARNING',
                'formatter': 'json_dated',
                'base_filename': str(paths['current'] / 'security.log'),
                'dated_path': str(paths['current_date']),
                'when': 'midnight',
                'interval': 1,
                'backupCount': 90,  # Mantener logs de seguridad más tiempo
                'encoding': 'utf8',
                'compress_after_days': 14
            },
            'file_error_dated': {
                'class': 'app.utils.log_config.DatedTimedRotatingFileHandler',
                'level': 'ERROR',
                'formatter': 'json_dated',
                'base_filename': str(paths['current'] / 'errors.log'),
                'dated_path': str(paths['current_date']),
                'when': 'midnight',
                'interval': 1,
                'backupCount': 60,
                'encoding': 'utf8',
                'compress_after_days': 30
            }
        }
        
        config['loggers'] = {
            'whatsapp_api': {
                'level': 'INFO',
                'handlers': ['file_app_dated', 'file_error_dated'],
                'propagate': False
            },
            'whatsapp_webhook': {
                'level': 'INFO',
                'handlers': ['file_app_dated', 'file_error_dated'],
                'propagate': False
            },
            'whatsapp_service': {
                'level': 'INFO',
                'handlers': ['file_app_dated', 'file_error_dated'],
                'propagate': False
            },
            'whatsapp_security': {
                'level': 'WARNING',
                'handlers': ['file_security_dated', 'file_error_dated'],
                'propagate': False
            }
        }
        
        config['root'] = {
            'level': 'WARNING',
            'handlers': ['console_error', 'file_error_dated']
        }
        
        return config


class DatedRotatingFileHandler(logging.handlers.RotatingFileHandler):
    """
    Handler personalizado que maneja archivos de log organizados por fecha
    """
    
    def __init__(self, base_filename, dated_filename, maxBytes=0, backupCount=0, encoding=None, delay=False):
        """
        Inicializa handler con soporte para fechas
        
        Args:
            base_filename: Archivo base (enlace simbólico)
            dated_filename: Archivo con fecha específica
            maxBytes: Tamaño máximo antes de rotar
            backupCount: Número de backups a mantener
        """
        self.base_filename = base_filename
        self.dated_filename = dated_filename
        self.current_date = datetime.now().date()
        
        # Crear enlace simbólico al archivo con fecha
        self._create_symlink()
        
        # Inicializar con el archivo con fecha
        super().__init__(dated_filename, 'a', maxBytes, backupCount, encoding, delay)
    
    def _create_symlink(self):
        """
        Crea enlace simbólico del archivo base al archivo con fecha
        """
        try:
            base_path = Path(self.base_filename)
            dated_path = Path(self.dated_filename)
            
            # Crear directorio padre si no existe
            base_path.parent.mkdir(parents=True, exist_ok=True)
            dated_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Remover enlace existente si existe
            if base_path.is_symlink() or base_path.exists():
                base_path.unlink(missing_ok=True)
            
            # Crear nuevo enlace simbólico (en Windows usar copia)
            if os.name == 'nt':
                # En Windows, hacer copia en lugar de symlink
                if dated_path.exists():
                    shutil.copy2(str(dated_path), str(base_path))
            else:
                # En Unix, crear symlink
                base_path.symlink_to(dated_path)
                
        except Exception as e:
            # Si falla, continuar sin symlink
            pass
    
    def emit(self, record):
        """
        Emite record verificando si cambió la fecha
        """
        current_date = datetime.now().date()
        
        # Si cambió la fecha, crear nuevo archivo
        if current_date != self.current_date:
            self.current_date = current_date
            
            # Actualizar nombres de archivo
            base_dir = Path(self.dated_filename).parent.parent.parent
            new_date_dir = base_dir / str(current_date.year) / f"{current_date.month:02d}" / f"{current_date.day:02d}"
            new_date_dir.mkdir(parents=True, exist_ok=True)
            
            # Obtener componente del nombre del archivo
            component = Path(self.dated_filename).stem.split('_')[0]
            new_dated_filename = str(new_date_dir / DateBasedLoggingConfig.get_dated_log_filename(component, current_date))
            
            # Cerrar archivo actual
            if self.stream:
                self.stream.close()
                self.stream = None
            
            # Actualizar filename
            self.dated_filename = new_dated_filename
            self.baseFilename = new_dated_filename
            
            # Crear nuevo symlink
            self._create_symlink()
        
        # Llamar al método padre
        super().emit(record)


class DatedTimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    """
    Handler con rotación temporal y organización por fechas para producción
    """
    
    def __init__(self, base_filename, dated_path, when='h', interval=1, 
                 backupCount=0, encoding=None, delay=False, utc=False, 
                 atTime=None, compress_after_days=7):
        """
        Handler con rotación temporal y compresión automática
        
        Args:
            compress_after_days: Días después de los cuales comprimir logs
        """
        self.dated_path = Path(dated_path)
        self.compress_after_days = compress_after_days
        
        # Generar filename con fecha actual
        component = Path(base_filename).stem
        today_filename = str(self.dated_path / DateBasedLoggingConfig.get_dated_log_filename(component))
        
        super().__init__(today_filename, when, interval, backupCount, encoding, delay, utc, atTime)
        
        # Crear enlace simbólico
        self._create_current_symlink(base_filename)
    
    def _create_current_symlink(self, base_filename):
        """
        Crea enlace simbólico al archivo actual
        """
        try:
            base_path = Path(base_filename)
            base_path.parent.mkdir(parents=True, exist_ok=True)
            
            if base_path.is_symlink() or base_path.exists():
                base_path.unlink(missing_ok=True)
            
            if os.name != 'nt':
                base_path.symlink_to(Path(self.baseFilename))
        except Exception:
            pass
    
    def doRollover(self):
        """
        Ejecuta rotación y compresión de logs antiguos
        """
        super().doRollover()
        
        # Comprimir logs antiguos
        self._compress_old_logs()
        
        # Limpiar logs muy antiguos
        self._cleanup_old_logs()
    
    def _compress_old_logs(self):
        """
        Comprime logs más antiguos que compress_after_days
        """
        if self.compress_after_days <= 0:
            return
        
        cutoff_date = datetime.now() - timedelta(days=self.compress_after_days)
        
        # Buscar archivos a comprimir
        log_pattern = Path(self.baseFilename).name.replace('.log', '*.log')
        
        for log_file in self.dated_path.parent.rglob(log_pattern):
            if log_file.suffix == '.log':
                try:
                    # Obtener fecha del archivo
                    file_date = datetime.fromtimestamp(log_file.stat().st_mtime)
                    
                    if file_date < cutoff_date:
                        # Comprimir archivo
                        compressed_file = log_file.with_suffix('.log.gz')
                        
                        with open(log_file, 'rb') as f_in:
                            with gzip.open(compressed_file, 'wb') as f_out:
                                shutil.copyfileobj(f_in, f_out)
                        
                        # Eliminar archivo original
                        log_file.unlink()
                        
                except Exception:
                    # Continuar si hay error con un archivo específico
                    continue
    
    def _cleanup_old_logs(self):
        """
        Elimina logs muy antiguos (más allá del backupCount)
        """
        if self.backupCount <= 0:
            return
        
        cutoff_date = datetime.now() - timedelta(days=self.backupCount)
        
        # Buscar y eliminar archivos muy antiguos
        for date_dir in self.dated_path.parent.parent.iterdir():
            if date_dir.is_dir() and date_dir.name.isdigit():
                try:
                    year = int(date_dir.name)
                    for month_dir in date_dir.iterdir():
                        if month_dir.is_dir():
                            month = int(month_dir.name)
                            for day_dir in month_dir.iterdir():
                                if day_dir.is_dir():
                                    day = int(day_dir.name)
                                    dir_date = datetime(year, month, day)
                                    
                                    if dir_date < cutoff_date:
                                        # Eliminar directorio completo
                                        shutil.rmtree(day_dir, ignore_errors=True)
                                        
                except Exception:
                    continue


class LogArchiveManager:
    """
    Gestor de archivado y limpieza de logs por fechas
    """
    
    def __init__(self, base_log_dir: str = 'logs'):
        self.base_log_dir = Path(base_log_dir)
        self.archive_dir = self.base_log_dir / 'archive'
        self.compressed_dir = self.base_log_dir / 'compressed'
        
        # Crear directorios si no existen
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        self.compressed_dir.mkdir(parents=True, exist_ok=True)
    
    def compress_logs_older_than(self, days: int = 7):
        """
        Comprime logs más antiguos que X días
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for year_dir in self.base_log_dir.iterdir():
            if year_dir.is_dir() and year_dir.name.isdigit():
                self._process_year_directory(year_dir, cutoff_date)
    
    def _process_year_directory(self, year_dir: Path, cutoff_date: datetime):
        """
        Procesa directorio de año para compresión
        """
        year = int(year_dir.name)
        
        for month_dir in year_dir.iterdir():
            if month_dir.is_dir() and month_dir.name.isdigit():
                month = int(month_dir.name)
                
                for day_dir in month_dir.iterdir():
                    if day_dir.is_dir() and day_dir.name.isdigit():
                        day = int(day_dir.name)
                        dir_date = datetime(year, month, day)
                        
                        if dir_date < cutoff_date:
                            self._compress_directory(day_dir, dir_date)
    
    def _compress_directory(self, day_dir: Path, date: datetime):
        """
        Comprime todos los logs de un día específico
        """
        try:
            # Crear archivo tar.gz con todos los logs del día
            date_str = date.strftime('%Y-%m-%d')
            archive_name = f"logs_{date_str}.tar.gz"
            archive_path = self.compressed_dir / archive_name
            
            import tarfile
            
            with tarfile.open(archive_path, "w:gz") as tar:
                for log_file in day_dir.glob("*.log"):
                    tar.add(log_file, arcname=f"{date_str}/{log_file.name}")
            
            # Eliminar directorio original después de comprimir
            shutil.rmtree(day_dir, ignore_errors=True)
            
        except Exception as e:
            # Log error pero continuar
            pass
    
    def cleanup_compressed_logs(self, retention_days: int = 365):
        """
        Elimina logs comprimidos más antiguos que retention_days
        """
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        for compressed_file in self.compressed_dir.glob("logs_*.tar.gz"):
            try:
                # Extraer fecha del nombre del archivo
                date_str = compressed_file.stem.replace("logs_", "").replace(".tar", "")
                file_date = datetime.strptime(date_str, '%Y-%m-%d')
                
                if file_date < cutoff_date:
                    compressed_file.unlink()
                    
            except Exception:
                continue


# Funciones de utilidad
def setup_dated_logging(environment: str = 'development', dual_output: bool = True):
    """
    Configura logging con estructura por fechas y salida dual
    """
    config_map = {
        'development': DateBasedLoggingConfig.get_development_config_with_dates,
        'production': DateBasedLoggingConfig.get_production_config_with_dates,
        'testing': DateBasedLoggingConfig.get_development_config_with_dates  # Usar dev para testing
    }
    
    config_func = config_map.get(environment, DateBasedLoggingConfig.get_development_config_with_dates)
    config = config_func(dual_output=dual_output)
    
    logging.config.dictConfig(config)
    
    return config


def create_log_maintenance_task():
    """
    Crea tarea de mantenimiento para logs
    """
    archive_manager = LogArchiveManager()
    
    def maintenance_task():
        # Comprimir logs de más de 7 días
        archive_manager.compress_logs_older_than(days=7)
        
        # Limpiar logs comprimidos de más de 1 año
        archive_manager.cleanup_compressed_logs(retention_days=365)
    
    return maintenance_task


# Función principal de inicialización
def initialize_dated_logging(app_config=None, environment: str = None, dual_output: bool = True):
    """
    Inicializa el sistema de logging completo con estructura por fechas
    Soporta salida dual: terminal en tiempo real + persistencia en archivos
    """
    if environment is None:
        environment = os.getenv('FLASK_ENV', 'development')
    
    # Configurar logging con fechas
    config = setup_dated_logging(environment, dual_output=dual_output)
    
    # Crear tarea de mantenimiento
    maintenance_task = create_log_maintenance_task()
    
    # En producción, programar tarea de mantenimiento
    if environment == 'production':
        try:
            import threading
            import time
            
            def run_maintenance():
                while True:
                    time.sleep(86400)  # 24 horas
                    try:
                        maintenance_task()
                    except Exception:
                        pass
            
            # Ejecutar tarea en background
            maintenance_thread = threading.Thread(target=run_maintenance, daemon=True)
            maintenance_thread.start()
            
        except Exception:
            # Si falla, continuar sin mantenimiento automático
            pass
    
    return {
        'environment': environment,
        'config': config,
        'maintenance_task': maintenance_task,
        'dated_structure': True
    }
    
    @staticmethod
    def get_development_config() -> Dict[str, Any]:
        """
        Configuración para entorno de desarrollo
        """
        config = LoggingConfig.get_base_config()
        
        # Crear directorio de logs si no existe
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        config['handlers'] = {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
                'formatter': 'detailed',
                'stream': 'ext://sys.stdout'
            },
            'file_rotating': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'DEBUG',
                'formatter': 'detailed',
                'filename': str(log_dir / 'whatsapp_api_dev.log'),
                'maxBytes': 10485760,  # 10MB
                'backupCount': 3,
                'encoding': 'utf8'
            }
        }
        
        config['loggers'] = {
            'whatsapp_api': {
                'level': 'DEBUG',
                'handlers': ['console', 'file_rotating'],
                'propagate': False
            },
            'whatsapp_webhook': {
                'level': 'DEBUG',
                'handlers': ['console', 'file_rotating'],
                'propagate': False
            },
            'whatsapp_service': {
                'level': 'DEBUG',
                'handlers': ['console', 'file_rotating'],
                'propagate': False
            },
            'whatsapp_database': {
                'level': 'INFO',
                'handlers': ['console', 'file_rotating'],
                'propagate': False
            }
        }
        
        config['root'] = {
            'level': 'INFO',
            'handlers': ['console', 'file_rotating']
        }
        
        return config
    
    @staticmethod
    def get_testing_config() -> Dict[str, Any]:
        """
        Configuración para entorno de testing
        """
        config = LoggingConfig.get_base_config()
        
        # En testing, solo log crítico a archivo, debug a console
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        config['handlers'] = {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'WARNING',
                'formatter': 'standard',
                'stream': 'ext://sys.stdout'
            },
            'test_file': {
                'class': 'logging.FileHandler',
                'level': 'ERROR',
                'formatter': 'json_simple',
                'filename': str(log_dir / 'whatsapp_api_test.log'),
                'mode': 'a',
                'encoding': 'utf8'
            }
        }
        
        config['loggers'] = {
            'whatsapp_api': {
                'level': 'WARNING',
                'handlers': ['console', 'test_file'],
                'propagate': False
            },
            'whatsapp_webhook': {
                'level': 'WARNING',
                'handlers': ['test_file'],
                'propagate': False
            },
            'whatsapp_service': {
                'level': 'WARNING',
                'handlers': ['test_file'],
                'propagate': False
            }
        }
        
        config['root'] = {
            'level': 'WARNING',
            'handlers': ['console']
        }
        
        return config
    
    @staticmethod
    def get_production_config() -> Dict[str, Any]:
        """
        Configuración para entorno de producción
        """
        config = LoggingConfig.get_base_config()
        
        log_dir = Path('/var/log/whatsapp-api') if os.name == 'posix' else Path('logs')
        log_dir.mkdir(exist_ok=True, parents=True)
        
        config['handlers'] = {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'ERROR',
                'formatter': 'json_simple',
                'stream': 'ext://sys.stdout'
            },
            'app_file': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'level': 'INFO',
                'formatter': 'json',
                'filename': str(log_dir / 'whatsapp_api.log'),
                'when': 'midnight',
                'interval': 1,
                'backupCount': 30,
                'encoding': 'utf8'
            },
            'security_file': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'level': 'WARNING',
                'formatter': 'json',
                'filename': str(log_dir / 'security.log'),
                'when': 'midnight',
                'interval': 1,
                'backupCount': 90,  # Mantener logs de seguridad más tiempo
                'encoding': 'utf8'
            },
            'error_file': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'level': 'ERROR',
                'formatter': 'json',
                'filename': str(log_dir / 'errors.log'),
                'when': 'midnight',
                'interval': 1,
                'backupCount': 60,
                'encoding': 'utf8'
            }
        }
        
        config['loggers'] = {
            'whatsapp_api': {
                'level': 'INFO',
                'handlers': ['app_file', 'error_file'],
                'propagate': False
            },
            'whatsapp_webhook': {
                'level': 'INFO',
                'handlers': ['app_file', 'error_file'],
                'propagate': False
            },
            'whatsapp_service': {
                'level': 'INFO',
                'handlers': ['app_file', 'error_file'],
                'propagate': False
            },
            'whatsapp_database': {
                'level': 'WARNING',
                'handlers': ['app_file', 'error_file'],
                'propagate': False
            },
            'whatsapp_security': {
                'level': 'WARNING',
                'handlers': ['security_file', 'error_file'],
                'propagate': False
            },
            'whatsapp_performance': {
                'level': 'INFO',
                'handlers': ['app_file'],
                'propagate': False
            }
        }
        
        config['root'] = {
            'level': 'WARNING',
            'handlers': ['console', 'error_file']
        }
        
        return config
    
    @staticmethod
    def get_docker_config() -> Dict[str, Any]:
        """
        Configuración específica para contenedores Docker
        """
        config = LoggingConfig.get_production_config()
        
        # En Docker, preferir stdout/stderr para integración con sistemas de logging
        config['handlers'] = {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'json',
                'stream': 'ext://sys.stdout'
            },
            'error_console': {
                'class': 'logging.StreamHandler',
                'level': 'ERROR',
                'formatter': 'json',
                'stream': 'ext://sys.stderr'
            }
        }
        
        # Simplificar loggers para Docker
        for logger_name in config['loggers']:
            config['loggers'][logger_name]['handlers'] = ['console', 'error_console']
        
        config['root']['handlers'] = ['console']
        
        return config
    
    @staticmethod
    def configure_for_environment(environment: str = None) -> None:
        """
        Configura logging basado en el entorno
        """
        if environment is None:
            environment = os.getenv('FLASK_ENV', 'development')
        
        config_map = {
            'development': LoggingConfig.get_development_config,
            'testing': LoggingConfig.get_testing_config,
            'production': LoggingConfig.get_production_config,
            'docker': LoggingConfig.get_docker_config
        }
        
        config_func = config_map.get(environment, LoggingConfig.get_development_config)
        config = config_func()
        
        logging.config.dictConfig(config)


class LogAggregationConfig:
    """
    Configuración para agregación y análisis de logs
    """
    
    @staticmethod
    def get_logstash_handler_config() -> Dict[str, Any]:
        """
        Configuración para envío de logs a Logstash/ELK Stack
        """
        return {
            'logstash': {
                'class': 'logstash.LogstashHandler',
                'level': 'INFO',
                'host': os.getenv('LOGSTASH_HOST', 'localhost'),
                'port': int(os.getenv('LOGSTASH_PORT', '5000')),
                'version': 1,
                'message_type': 'whatsapp_api',
                'fqdn': False,
                'tags': ['whatsapp-api', 'microservice']
            }
        }
    
    @staticmethod
    def get_fluentd_handler_config() -> Dict[str, Any]:
        """
        Configuración para envío de logs a Fluentd
        """
        return {
            'fluentd': {
                'class': 'fluent.handler.FluentHandler',
                'level': 'INFO',
                'tag': 'whatsapp.api',
                'host': os.getenv('FLUENTD_HOST', 'localhost'),
                'port': int(os.getenv('FLUENTD_PORT', '24224'))
            }
        }
    
    @staticmethod
    def get_syslog_handler_config() -> Dict[str, Any]:
        """
        Configuración para envío de logs vía syslog
        """
        return {
            'syslog': {
                'class': 'logging.handlers.SysLogHandler',
                'level': 'WARNING',
                'formatter': 'json',
                'address': ('localhost', 514),
                'facility': 'user'
            }
        }


class LogMonitoringConfig:
    """
    Configuración para monitoreo y alertas de logs
    """
    
    @staticmethod
    def setup_log_monitoring():
        """
        Configura monitoreo automático de logs críticos
        """
        # Configurar filtros para detectar patrones críticos
        critical_patterns = [
            'API_RATE_LIMIT_EXCEEDED',
            'WEBHOOK_SIGNATURE_INVALID',
            'DATABASE_CONNECTION_FAILED',
            'AUTHENTICATION_FAILED_MULTIPLE'
        ]
        
        return {
            'monitoring': {
                'enabled': os.getenv('LOG_MONITORING_ENABLED', 'false').lower() == 'true',
                'critical_patterns': critical_patterns,
                'alert_threshold': int(os.getenv('LOG_ALERT_THRESHOLD', '5')),  # Alertas después de 5 ocurrencias
                'alert_window_minutes': int(os.getenv('LOG_ALERT_WINDOW', '15'))  # En ventana de 15 minutos
            }
        }
    
    @staticmethod
    def get_health_check_logging_config():
        """
        Configuración específica para health checks y métricas
        """
        return {
            'health_check': {
                'log_successful_checks': os.getenv('LOG_HEALTH_SUCCESS', 'false').lower() == 'true',
                'log_failed_checks': True,
                'metrics_interval_seconds': int(os.getenv('METRICS_INTERVAL', '60'))
            }
        }


# Función utilitaria para inicializar logging
def initialize_logging(app_config=None, environment: str = None):
    """
    Inicializa el sistema de logging completo
    
    Args:
        app_config: Configuración de la aplicación Flask
        environment: Entorno de ejecución
    """
    if environment is None:
        environment = os.getenv('FLASK_ENV', 'development')
    
    # Configurar logging básico
    LoggingConfig.configure_for_environment(environment)
    
    # Configurar agregación si está habilitada
    if os.getenv('LOG_AGGREGATION_ENABLED', 'false').lower() == 'true':
        aggregation_type = os.getenv('LOG_AGGREGATION_TYPE', 'logstash')
        
        if aggregation_type == 'logstash':
            extra_handlers = LogAggregationConfig.get_logstash_handler_config()
        elif aggregation_type == 'fluentd':
            extra_handlers = LogAggregationConfig.get_fluentd_handler_config()
        elif aggregation_type == 'syslog':
            extra_handlers = LogAggregationConfig.get_syslog_handler_config()
        else:
            extra_handlers = {}
        
        # Agregar handlers de agregación a la configuración existente
        if extra_handlers:
            current_config = logging.getLogger().handlers
            for handler_name, handler_config in extra_handlers.items():
                # Aquí se agregarían los handlers adicionales
                pass
    
    # Configurar monitoreo si está habilitado
    monitoring_config = LogMonitoringConfig.setup_log_monitoring()
    
    return {
        'environment': environment,
        'monitoring': monitoring_config,
        'aggregation_enabled': os.getenv('LOG_AGGREGATION_ENABLED', 'false').lower() == 'true'
    }
