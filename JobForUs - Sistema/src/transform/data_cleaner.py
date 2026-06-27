"""
Módulo de limpieza de datos (versión original)
JobForUs - Sistema de Inteligencia de Mercado Laboral
"""

import pandas as pd


class DataCleaner:
    """
    Clase encargada de limpiar y validar los datos extraídos.
    (Versión original - mantiene compatibilidad)
    """
    
    def __init__(self):
        self.logs = []
        self.estadisticas = {}
    
    def _log(self, message):
        self.logs.append(message)
        print(f"   {message}")
    
    def limpiar_dataset(self, df):
        """Limpia el dataset eliminando registros no válidos."""
        self._log("🧹 Iniciando limpieza de datos...")
        registros_iniciales = len(df)
        
        # Eliminar filas sin título
        if 'job_title' in df.columns:
            antes = len(df)
            df = df[df['job_title'].notna()]
            self._log(f"   - Eliminados {antes - len(df)} filas sin título")
        
        # Eliminar duplicados básicos
        antes = len(df)
        df = df.drop_duplicates()
        self._log(f"   - Eliminados {antes - len(df)} duplicados")
        
        self.estadisticas = {
            'registros_iniciales': registros_iniciales,
            'registros_finales': len(df),
            'eliminados': registros_iniciales - len(df)
        }
        
        self._log(f"\n✅ Limpieza completada: {len(df)} registros")
        return df
    
    def obtener_logs(self):
        return self.logs
    
    def obtener_estadisticas(self):
        return self.estadisticas