"""
Módulo de clasificación de seniority (versión original)
JobForUs - Sistema de Inteligencia de Mercado Laboral
"""

import pandas as pd


class SeniorityClassifier:
    """
    Clase encargada de clasificar el seniority.
    (Versión original - mantiene compatibilidad)
    """
    
    def __init__(self):
        self.logs = []
        self.reglas = {
            'Junior': (0, 2),
            'Mid': (3, 5),
            'Senior': (6, 9),
            'Lead': (10, 99)
        }
    
    def _log(self, message):
        self.logs.append(message)
        print(f"   {message}")
    
    def clasificar_por_experiencia(self, años):
        if pd.isna(años):
            return 'No especificado'
        for nivel, (min_años, max_años) in self.reglas.items():
            if min_años <= años <= max_años:
                return nivel
        return 'No especificado'
    
    def clasificar_dataset(self, df):
        """Clasifica todo el dataset agregando columna 'seniority'."""
        self._log("🏷️ Clasificando seniority...")
        
        df_clasificado = df.copy()
        
        if 'experience_required' in df_clasificado.columns:
            df_clasificado['seniority'] = df_clasificado['experience_required'].apply(
                self.clasificar_por_experiencia
            )
        elif 'experience_level' in df_clasificado.columns:
            # Mapear experience_level a nombres amigables
            mapeo = {
                'Entry (0-2 yrs)': 'Junior',
                'Mid (3-5 yrs)': 'Mid', 
                'Senior (6-10 yrs)': 'Senior',
                'Lead (11-15 yrs)': 'Lead'
            }
            df_clasificado['seniority'] = df_clasificado['experience_level'].map(mapeo)
            df_clasificado['seniority'] = df_clasificado['seniority'].fillna('No especificado')
        else:
            df_clasificado['seniority'] = 'No especificado'
        
        distribucion = df_clasificado['seniority'].value_counts()
        self._log(f"\n   📊 Distribución de seniority:")
        for nivel, cantidad in distribucion.items():
            self._log(f"      - {nivel}: {cantidad} registros")
        
        return df_clasificado
    
    def obtener_logs(self):
        return self.logs