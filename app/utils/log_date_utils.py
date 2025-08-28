"""
Utilidades para gestión de logs organizados por fecha
Funciones para búsqueda, análisis y mantenimiento de logs históricos
"""

import os
import json
import gzip
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Generator
import re


class LogDateManager:
    """
    Gestor para navegación y búsqueda en logs organizados por fecha
    """
    
    def __init__(self, base_log_dir: str = 'logs'):
        self.base_log_dir = Path(base_log_dir)
        
    def get_available_dates(self) -> List[datetime]:
        """
        Obtiene lista de fechas disponibles en los logs
        
        Returns:
            Lista de fechas ordenadas para las cuales existen logs
        """
        dates = []
        
        for year_dir in self.base_log_dir.iterdir():
            if year_dir.is_dir() and year_dir.name.isdigit():
                year = int(year_dir.name)
                
                for month_dir in year_dir.iterdir():
                    if month_dir.is_dir() and month_dir.name.isdigit():
                        month = int(month_dir.name)
                        
                        for day_dir in month_dir.iterdir():
                            if day_dir.is_dir() and day_dir.name.isdigit():
                                day = int(day_dir.name)
                                try:
                                    date = datetime(year, month, day)
                                    dates.append(date)
                                except ValueError:
                                    continue
        
        return sorted(dates)
    
    def get_logs_for_date(self, date: datetime, component: str = None) -> List[Path]:
        """
        Obtiene archivos de log para una fecha específica
        
        Args:
            date: Fecha para buscar logs
            component: Componente específico (api, webhook, service, etc.)
            
        Returns:
            Lista de archivos de log para la fecha
        """
        date_path = self._get_date_path(date)
        
        if not date_path.exists():
            return []
        
        if component:
            # Buscar archivos específicos del componente
            pattern = f"{component}_*.log*"
        else:
            # Buscar todos los archivos de log
            pattern = "*.log*"
        
        return list(date_path.glob(pattern))
    
    def get_logs_for_date_range(self, start_date: datetime, end_date: datetime, 
                               component: str = None) -> List[Path]:
        """
        Obtiene logs para un rango de fechas
        
        Args:
            start_date: Fecha de inicio
            end_date: Fecha final
            component: Componente específico opcional
            
        Returns:
            Lista de archivos de log en el rango
        """
        logs = []
        current_date = start_date
        
        while current_date <= end_date:
            logs.extend(self.get_logs_for_date(current_date, component))
            current_date += timedelta(days=1)
        
        return sorted(logs)
    
    def _get_date_path(self, date: datetime) -> Path:
        """
        Construye path para una fecha específica
        """
        return self.base_log_dir / str(date.year) / f"{date.month:02d}" / f"{date.day:02d}"
    
    def search_logs_by_pattern(self, pattern: str, start_date: datetime = None, 
                              end_date: datetime = None, component: str = None) -> Generator[Dict[str, Any], None, None]:
        """
        Busca patrón en logs de un rango de fechas
        
        Args:
            pattern: Patrón regex a buscar
            start_date: Fecha de inicio (default: hace 7 días)
            end_date: Fecha final (default: hoy)
            component: Componente específico
            
        Yields:
            Dict con información de matches encontrados
        """
        if start_date is None:
            start_date = datetime.now() - timedelta(days=7)
        if end_date is None:
            end_date = datetime.now()
        
        compiled_pattern = re.compile(pattern, re.IGNORECASE)
        log_files = self.get_logs_for_date_range(start_date, end_date, component)
        
        for log_file in log_files:
            for line_num, line, timestamp in self._read_log_file(log_file):
                if compiled_pattern.search(line):
                    yield {
                        'file': str(log_file),
                        'line_number': line_num,
                        'line': line.strip(),
                        'timestamp': timestamp,
                        'date': self._extract_date_from_path(log_file)
                    }
    
    def _read_log_file(self, log_file: Path) -> Generator[tuple, None, None]:
        """
        Lee archivo de log (normal o comprimido)
        
        Yields:
            Tupla (line_number, line, timestamp)
        """
        try:
            if log_file.suffix == '.gz':
                opener = gzip.open
                mode = 'rt'
            else:
                opener = open
                mode = 'r'
            
            with opener(log_file, mode, encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    timestamp = self._extract_timestamp_from_line(line)
                    yield (line_num, line, timestamp)
                    
        except Exception:
            # Si hay error leyendo el archivo, continuar
            pass
    
    def _extract_timestamp_from_line(self, line: str) -> Optional[datetime]:
        """
        Extrae timestamp de una línea de log
        """
        try:
            # Para logs JSON estructurados
            if line.strip().startswith('{'):
                log_data = json.loads(line)
                if 'timestamp' in log_data:
                    return datetime.fromisoformat(log_data['timestamp'].replace('Z', '+00:00'))
            
            # Para logs con formato estándar
            timestamp_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})'
            match = re.search(timestamp_pattern, line)
            if match:
                return datetime.strptime(match.group(1), '%Y-%m-%d %H:%M:%S')
                
        except Exception:
            pass
        
        return None
    
    def _extract_date_from_path(self, log_file: Path) -> datetime:
        """
        Extrae fecha del path del archivo de log
        """
        parts = log_file.parts
        try:
            # Buscar partes que representen año/mes/día
            for i, part in enumerate(parts):
                if part.isdigit() and len(part) == 4:  # Año
                    year = int(part)
                    month = int(parts[i + 1])
                    day = int(parts[i + 2])
                    return datetime(year, month, day)
        except (IndexError, ValueError):
            pass
        
        return datetime.now()
    
    def get_log_statistics(self, start_date: datetime = None, 
                          end_date: datetime = None) -> Dict[str, Any]:
        """
        Obtiene estadísticas de logs para un período
        
        Returns:
            Dict con estadísticas de logs
        """
        if start_date is None:
            start_date = datetime.now() - timedelta(days=30)
        if end_date is None:
            end_date = datetime.now()
        
        stats = {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'days': (end_date - start_date).days + 1
            },
            'files': {
                'total_count': 0,
                'total_size_bytes': 0,
                'by_component': {},
                'by_date': {}
            },
            'log_levels': {
                'ERROR': 0,
                'WARNING': 0,
                'INFO': 0,
                'DEBUG': 0
            }
        }
        
        log_files = self.get_logs_for_date_range(start_date, end_date)
        
        for log_file in log_files:
            # Estadísticas de archivos
            stats['files']['total_count'] += 1
            
            try:
                file_size = log_file.stat().st_size
                stats['files']['total_size_bytes'] += file_size
                
                # Por componente
                component = self._extract_component_from_filename(log_file.name)
                if component not in stats['files']['by_component']:
                    stats['files']['by_component'][component] = {'count': 0, 'size_bytes': 0}
                
                stats['files']['by_component'][component]['count'] += 1
                stats['files']['by_component'][component]['size_bytes'] += file_size
                
                # Por fecha
                date_key = self._extract_date_from_path(log_file).strftime('%Y-%m-%d')
                if date_key not in stats['files']['by_date']:
                    stats['files']['by_date'][date_key] = {'count': 0, 'size_bytes': 0}
                
                stats['files']['by_date'][date_key]['count'] += 1
                stats['files']['by_date'][date_key]['size_bytes'] += file_size
                
                # Analizar contenido para niveles de log
                self._analyze_log_levels(log_file, stats['log_levels'])
                
            except Exception:
                continue
        
        # Convertir tamaños a formato legible
        stats['files']['total_size_readable'] = self._format_file_size(stats['files']['total_size_bytes'])
        
        for component_stats in stats['files']['by_component'].values():
            component_stats['size_readable'] = self._format_file_size(component_stats['size_bytes'])
        
        for date_stats in stats['files']['by_date'].values():
            date_stats['size_readable'] = self._format_file_size(date_stats['size_bytes'])
        
        return stats
    
    def _extract_component_from_filename(self, filename: str) -> str:
        """
        Extrae nombre del componente del nombre del archivo
        """
        parts = filename.split('_')
        return parts[0] if parts else 'unknown'
    
    def _analyze_log_levels(self, log_file: Path, level_stats: Dict[str, int]):
        """
        Analiza niveles de log en un archivo
        """
        try:
            # Solo analizar una muestra para archivos grandes
            max_lines = 1000
            line_count = 0
            
            for _, line, _ in self._read_log_file(log_file):
                if line_count >= max_lines:
                    break
                
                line_count += 1
                
                # Buscar niveles de log
                for level in ['ERROR', 'WARNING', 'INFO', 'DEBUG']:
                    if level in line:
                        level_stats[level] += 1
                        break
                        
        except Exception:
            pass
    
    def _format_file_size(self, size_bytes: int) -> str:
        """
        Formatea tamaño de archivo en formato legible
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024**2:
            return f"{size_bytes/1024:.1f} KB"
        elif size_bytes < 1024**3:
            return f"{size_bytes/(1024**2):.1f} MB"
        else:
            return f"{size_bytes/(1024**3):.1f} GB"


class LogAnalyzer:
    """
    Analizador avanzado de logs por fecha
    """
    
    def __init__(self, base_log_dir: str = 'logs'):
        self.date_manager = LogDateManager(base_log_dir)
    
    def find_error_patterns(self, days_back: int = 7) -> Dict[str, List[Dict[str, Any]]]:
        """
        Encuentra patrones de errores en los últimos días
        
        Args:
            days_back: Días hacia atrás para analizar
            
        Returns:
            Dict con patrones de errores agrupados
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        error_patterns = {
            'database_errors': [],
            'api_errors': [],
            'authentication_errors': [],
            'general_errors': []
        }
        
        # Patrones a buscar
        patterns = {
            'database_errors': [
                r'database.*error',
                r'connection.*failed',
                r'sqlalchemy.*error'
            ],
            'api_errors': [
                r'whatsapp.*api.*error',
                r'http.*error.*[45]\d{2}',
                r'timeout.*error'
            ],
            'authentication_errors': [
                r'authentication.*failed',
                r'unauthorized.*access',
                r'invalid.*token'
            ]
        }
        
        # Buscar cada patrón
        for category, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = list(self.date_manager.search_logs_by_pattern(
                    pattern, start_date, end_date
                ))
                error_patterns[category].extend(matches)
        
        return error_patterns
    
    def analyze_performance_trends(self, days_back: int = 30) -> Dict[str, Any]:
        """
        Analiza tendencias de performance en los logs
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Buscar métricas de performance
        performance_pattern = r'response_time_ms.*?(\d+\.?\d*)'
        matches = list(self.date_manager.search_logs_by_pattern(
            performance_pattern, start_date, end_date
        ))
        
        # Agrupar por fecha
        daily_metrics = {}
        for match in matches:
            date_key = match['date'].strftime('%Y-%m-%d')
            
            if date_key not in daily_metrics:
                daily_metrics[date_key] = []
            
            # Extraer tiempo de respuesta
            response_time_match = re.search(r'response_time_ms.*?(\d+\.?\d*)', match['line'])
            if response_time_match:
                response_time = float(response_time_match.group(1))
                daily_metrics[date_key].append(response_time)
        
        # Calcular estadísticas
        trends = {}
        for date_key, times in daily_metrics.items():
            if times:
                trends[date_key] = {
                    'avg_response_time': sum(times) / len(times),
                    'max_response_time': max(times),
                    'min_response_time': min(times),
                    'request_count': len(times)
                }
        
        return {
            'period': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            'daily_trends': trends,
            'total_requests': sum(trend['request_count'] for trend in trends.values())
        }
    
    def generate_daily_report(self, date: datetime) -> Dict[str, Any]:
        """
        Genera reporte diario para una fecha específica
        """
        logs = self.date_manager.get_logs_for_date(date)
        
        report = {
            'date': date.strftime('%Y-%m-%d'),
            'files_count': len(logs),
            'components': set(),
            'log_levels': {'ERROR': 0, 'WARNING': 0, 'INFO': 0, 'DEBUG': 0},
            'key_events': [],
            'errors': [],
            'performance_summary': {}
        }
        
        for log_file in logs:
            component = self.date_manager._extract_component_from_filename(log_file.name)
            report['components'].add(component)
            
            # Analizar contenido
            for line_num, line, timestamp in self.date_manager._read_log_file(log_file):
                # Contar niveles
                for level in report['log_levels'].keys():
                    if level in line:
                        report['log_levels'][level] += 1
                
                # Buscar errores importantes
                if 'ERROR' in line:
                    report['errors'].append({
                        'file': log_file.name,
                        'line': line_num,
                        'message': line.strip()[:200],  # Primeros 200 chars
                        'timestamp': timestamp.isoformat() if timestamp else None
                    })
                
                # Eventos clave
                if any(keyword in line.lower() for keyword in ['message_sent', 'webhook_received', 'authentication']):
                    report['key_events'].append({
                        'type': self._classify_event(line),
                        'timestamp': timestamp.isoformat() if timestamp else None,
                        'details': line.strip()[:100]
                    })
        
        report['components'] = list(report['components'])
        return report
    
    def _classify_event(self, line: str) -> str:
        """
        Clasifica tipo de evento basado en el contenido de la línea
        """
        line_lower = line.lower()
        
        if 'message_sent' in line_lower:
            return 'message_sent'
        elif 'webhook_received' in line_lower:
            return 'webhook_received'
        elif 'authentication' in line_lower:
            return 'authentication'
        elif 'error' in line_lower:
            return 'error'
        else:
            return 'general'


def create_log_viewer_commands():
    """
    Crea comandos útiles para visualizar logs organizados por fecha
    """
    date_manager = LogDateManager()
    analyzer = LogAnalyzer()
    
    commands = {
        'list_dates': lambda: date_manager.get_available_dates(),
        'logs_for_today': lambda: date_manager.get_logs_for_date(datetime.now()),
        'logs_for_yesterday': lambda: date_manager.get_logs_for_date(datetime.now() - timedelta(days=1)),
        'search_errors_today': lambda: list(date_manager.search_logs_by_pattern(
            r'ERROR', datetime.now().replace(hour=0, minute=0, second=0)
        )),
        'weekly_stats': lambda: date_manager.get_log_statistics(
            datetime.now() - timedelta(days=7)
        ),
        'error_patterns': lambda: analyzer.find_error_patterns(),
        'performance_trends': lambda: analyzer.analyze_performance_trends(),
        'today_report': lambda: analyzer.generate_daily_report(datetime.now())
    }
    
    return commands
