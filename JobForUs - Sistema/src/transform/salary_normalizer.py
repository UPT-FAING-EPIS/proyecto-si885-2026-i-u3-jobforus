"""
Módulo de normalización de salarios (versión original)
JobForUs - Sistema de Inteligencia de Mercado Laboral
"""

import pandas as pd


class SalaryNormalizer:
    """
    Clase encargada de normalizar los salarios.
    (Versión original - mantiene compatibilidad)
    """
    
    def __init__(self):
        self.logs = []
    
    def _log(self, message):
        self.logs.append(message)
        print(f"   {message}")
    
    def normalizar_salarios(self, df):
        """Normaliza los salarios a USD mensuales."""
        self._log("💰 Normalizando salarios...")
        
        df_normalizado = df.copy()
        
        # Buscar columna de salario
        salario_col = None
        for col in ['salary_usd', 'base_salary_usd', 'salary', 'salario']:
            if col in df_normalizado.columns:
                salario_col = col
                break
        
        if salario_col:
            df_normalizado['salary_usd'] = pd.to_numeric(df_normalizado[salario_col], errors='coerce')
            self._log(f"   - Salarios normalizados desde columna '{salario_col}'")
            self._log(f"   - Salario promedio: ${df_normalizado['salary_usd'].mean():,.0f}")
        else:
            self._log("   - ⚠️ No se encontró columna de salario")
            df_normalizado['salary_usd'] = None
        
        return df_normalizado
    
    def obtener_logs(self):
        return self.logs