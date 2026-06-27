"""
Módulo de transformación de datos
JobForUs - Sistema de Inteligencia de Mercado Laboral

Este módulo contiene las clases para transformar los datos extraídos:
- DataCleaner: Limpieza básica de datos
- SalaryNormalizer: Normalización de salarios
- SeniorityClassifier: Clasificación de niveles de experiencia
- TechClassifier: Clasificación de tecnologías
- GlobalDatasetTransformer: Transformador específico para el dataset global (NUEVO)
"""

# Importar transformadores originales (para compatibilidad con dataset anterior)
from src.transform.data_cleaner import DataCleaner
from src.transform.salary_normalizer import SalaryNormalizer
from src.transform.seniority_classifier import SeniorityClassifier
from src.transform.tech_classifier import TechClassifier

# Importar nuevo transformador para dataset global
from src.transform.global_dataset_transformer import GlobalDatasetTransformer


# ============================================================
# TRANSFORMADOR COMPLETO (para dataset original)
# Mantenido por compatibilidad
# ============================================================

class TransformadorCompleto:
    """
    Transformador completo para el dataset original (job_market.csv).
    Ejecuta todo el pipeline: limpieza → normalización → seniority → tecnologías.
    """
    
    def __init__(self):
        self.logs = []
        self.cleaner = DataCleaner()
        self.normalizer = SalaryNormalizer()
        self.seniority_classifier = SeniorityClassifier()
        self.tech_classifier = TechClassifier()
    
    def _log(self, message):
        """Registra un mensaje en el log."""
        self.logs.append(message)
        print(message)
    
    def transformar(self, df):
        """
        Ejecuta el pipeline de transformación para dataset original.
        
        Args:
            df: DataFrame original
            
        Returns:
            DataFrame transformado
        """
        self._log("\n" + "=" * 60)
        self._log("🔄 INICIANDO TRANSFORMACIÓN (MODO ORIGINAL)")
        self._log("=" * 60)
        
        self._log("\n📌 Paso 1: Limpieza de datos")
        df = self.cleaner.limpiar_dataset(df)
        
        self._log("\n📌 Paso 2: Normalización de salarios")
        df = self.normalizer.normalizar_salarios(df)
        
        self._log("\n📌 Paso 3: Clasificación de seniority")
        df = self.seniority_classifier.clasificar_dataset(df)
        
        self._log("\n📌 Paso 4: Clasificación de tecnologías")
        df = self.tech_classifier.clasificar_dataset(df)
        
        self._log("\n" + "=" * 60)
        self._log("✅ TRANSFORMACIÓN COMPLETADA")
        self._log(f"📊 Dataset final: {len(df)} registros, {len(df.columns)} columnas")
        self._log("=" * 60)
        
        return df
    
    def obtener_logs(self):
        """Retorna los logs del proceso."""
        return self.logs


# ============================================================
# TRANSFORMADOR PARA DATASET GLOBAL
# ============================================================

class TransformadorGlobal:
    """
    Transformador específico para el dataset global (global_ai_tech_salaries_2020_2025.csv).
    """
    
    def __init__(self):
        self.transformer = GlobalDatasetTransformer()
    
    def transformar(self, df, aplicar_filtro_latam=False, guardar_resultado=False):
        """
        Ejecuta el pipeline de transformación para dataset global.
        
        Args:
            df: DataFrame original
            aplicar_filtro_latam: Si es True, filtra solo países LATAM
            guardar_resultado: Si es True, guarda el resultado en CSV
            
        Returns:
            DataFrame transformado
        """
        return self.transformer.transformar_completo(
            df, 
            aplicar_filtro_latam=aplicar_filtro_latam,
            guardar_resultado=guardar_resultado
        )
    
    def obtener_logs(self):
        """Retorna los logs del proceso."""
        return self.transformer.obtener_logs()
    
    def obtener_estadisticas(self):
        """Retorna las estadísticas del proceso."""
        return self.transformer.obtener_estadisticas()


# ============================================================
# FUNCIONES DE UTILIDAD
# ============================================================

def transformar_segun_dataset(df, dataset_tipo='global'):
    """
    Selecciona automáticamente el transformador según el tipo de dataset.
    
    Args:
        df: DataFrame a transformar
        dataset_tipo: 'global' para dataset global, 'original' para job_market.csv
        
    Returns:
        DataFrame transformado
    """
    if dataset_tipo == 'global':
        transformer = TransformadorGlobal()
        return transformer.transformar(df)
    else:
        transformer = TransformadorCompleto()
        return transformer.transformar(df)


def identificar_tipo_dataset(df):
    """
    Intenta identificar automáticamente qué tipo de dataset es.
    
    Args:
        df: DataFrame a analizar
        
    Returns:
        String: 'global' o 'original'
    """
    # Columnas características del dataset global
    columnas_global = ['base_salary_usd', 'total_compensation_usd', 'survey_year', 'job_category']
    
    # Columnas características del dataset original
    columnas_original = ['salary_min', 'salary_max', 'publication_date', 'benefits']
    
    for col in columnas_global:
        if col in df.columns:
            return 'global'
    
    for col in columnas_original:
        if col in df.columns:
            return 'original'
    
    return 'original'  # Por defecto


# ============================================================
# EXPORTAR CLASES PRINCIPALES
# ============================================================

__all__ = [
    'DataCleaner',
    'SalaryNormalizer', 
    'SeniorityClassifier',
    'TechClassifier',
    'GlobalDatasetTransformer',
    'TransformadorCompleto',
    'TransformadorGlobal',
    'transformar_segun_dataset',
    'identificar_tipo_dataset'
]