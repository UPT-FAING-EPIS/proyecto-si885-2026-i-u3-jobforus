"""
Módulo de carga de datos a SQLite
JobForUs - Sistema de Inteligencia de Mercado Laboral

Este módulo contiene la clase DatabaseLoader que se encarga de:
- Conectar a la base de datos SQLite
- Crear las tablas según el esquema definido
- Insertar datos en las tablas de dimensiones y hechos
- Manejar la integridad referencial
"""

import sqlite3
import pandas as pd
import os
from datetime import datetime


class DatabaseLoader:
    """
    Clase encargada de cargar los datos transformados a SQLite.
    """
    
    def __init__(self, db_path="database/job_market.db"):
        """
        Inicializa el cargador con la ruta de la base de datos.
        
        Args:
            db_path: Ruta al archivo de base de datos SQLite
        """
        # Obtener la ruta absoluta del proyecto
        script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.db_path = os.path.join(script_dir, db_path)
        self.connection = None
        self.cursor = None
        self.logs = []
        
        # Asegurar que el directorio database existe
        db_dir = os.path.dirname(self.db_path)
        os.makedirs(db_dir, exist_ok=True)
    
    def _log(self, message):
        """Registra un mensaje en el log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)
        print(log_entry)
    
    def conectar(self):
        """
        Establece conexión con la base de datos SQLite.
        
        Returns:
            True si la conexión fue exitosa, False en caso contrario
        """
        try:
            self._log(f"🔌 Conectando a base de datos: {self.db_path}")
            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()
            self._log("✅ Conexión establecida")
            return True
        except Exception as e:
            self._log(f"❌ Error al conectar: {e}")
            return False
    
    def crear_tablas(self, schema_path="database/schema.sql"):
        """
        Crea las tablas ejecutando el script schema.sql.
        """
        try:
            script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            schema_full_path = os.path.join(script_dir, schema_path)
            
            self._log(f"📝 Creando tablas desde: {schema_full_path}")
            
            # PRIMERO: Eliminar vistas existentes
            vistas = [
                "vw_salario_por_tecnologia", "vw_salario_por_seniority", 
                "vw_tecnologias_demandadas", "vw_salario_por_genero",
                "vw_salario_por_work_setting", "vw_evolucion_salarial",
                "vw_adopcion_ia_por_anio", "vw_satisfaccion_por_seniority"
            ]
            for vista in vistas:
                try:
                    self.cursor.execute(f"DROP VIEW IF EXISTS {vista}")
                except:
                    pass
            self.connection.commit()
            
            # SEGUNDO: Ejecutar el schema.sql
            with open(schema_full_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            self.cursor.executescript(schema_sql)
            self.connection.commit()
            
            self._log("✅ Tablas y vistas creadas correctamente")
            return True
            
        except Exception as e:
            self._log(f"❌ Error al crear tablas: {e}")
            return False
    
    def obtener_seniority_id(self, seniority_texto):
        """
        Obtiene el ID de seniority basado en el texto.
        
        Args:
            seniority_texto: Nivel de seniority (Junior, Mid, Senior, Lead)
            
        Returns:
            ID del seniority (1-5)
        """
        seniority_map = {
            'Junior': 1,
            'Mid': 2,
            'Senior': 3,
            'Lead': 4,
            'No especificado': 5
        }
        return seniority_map.get(seniority_texto, 5)
    
    def insertar_dimensiones(self, df):
        """
        Inserta los datos únicos en las tablas de dimensiones.
        
        Args:
            df: DataFrame con los datos transformados
            
        Returns:
            Diccionario con los mapeos de IDs
        """
        self._log("\n📥 Insertando dimensiones...")
        
        mapeos = {
            'tecnologia': {},
            'empresa': {},
            'ubicacion': {}
        }
        
        # 1. Insertar tecnologías únicas
        if 'tecnologia_principal' in df.columns:
            tech_data = df[['tecnologia_principal', 'categoria_principal']].drop_duplicates()
            tech_data = tech_data[tech_data['tecnologia_principal'].notna()]
            tech_data = tech_data[tech_data['tecnologia_principal'] != 'Sin tecnología']
            tech_data = tech_data[tech_data['tecnologia_principal'] != 'No disponible']
            
            for _, row in tech_data.iterrows():
                tech = row['tecnologia_principal']
                categoria = row['categoria_principal']
                try:
                    self.cursor.execute(
                        "INSERT OR IGNORE INTO dim_tecnologia (nombre, categoria) VALUES (?, ?)",
                        (tech, categoria)
                    )
                    self.cursor.execute("SELECT tecnologia_id FROM dim_tecnologia WHERE nombre = ?", (tech,))
                    row_result = self.cursor.fetchone()
                    if row_result:
                        mapeos['tecnologia'][tech] = row_result[0]
                except Exception as e:
                    self._log(f"   ⚠️ Error insertando tecnología {tech}: {e}")
            
            self._log(f"   ✅ Tecnologías insertadas: {len(mapeos['tecnologia'])}")
        
        # 2. Insertar empresas (si existe columna company)
        if 'company' in df.columns:
            empresas_unicas = df['company'].dropna().unique()
            for empresa in empresas_unicas:
                try:
                    self.cursor.execute(
                        "INSERT OR IGNORE INTO dim_empresa (nombre) VALUES (?)",
                        (empresa,)
                    )
                    self.cursor.execute("SELECT empresa_id FROM dim_empresa WHERE nombre = ?", (empresa,))
                    row_result = self.cursor.fetchone()
                    if row_result:
                        mapeos['empresa'][empresa] = row_result[0]
                except Exception as e:
                    self._log(f"   ⚠️ Error insertando empresa {empresa}: {e}")
            
            self._log(f"   ✅ Empresas insertadas: {len(mapeos['empresa'])}")
        
        # 3. Insertar ubicaciones (países del dataset global)
        if 'country' in df.columns:
            ubicaciones_unicas = df['country'].dropna().unique()
            for ubicacion in ubicaciones_unicas:
                try:
                    self.cursor.execute(
                        "INSERT OR IGNORE INTO dim_ubicacion (nombre_completo, pais) VALUES (?, ?)",
                        (ubicacion, ubicacion)
                    )
                    self.cursor.execute("SELECT ubicacion_id FROM dim_ubicacion WHERE nombre_completo = ?", (ubicacion,))
                    row_result = self.cursor.fetchone()
                    if row_result:
                        mapeos['ubicacion'][ubicacion] = row_result[0]
                except Exception as e:
                    self._log(f"   ⚠️ Error insertando ubicación {ubicacion}: {e}")
            
            self._log(f"   ✅ Ubicaciones insertadas: {len(mapeos['ubicacion'])}")
        
        self.connection.commit()
        return mapeos
    
    def insertar_hechos(self, df, mapeos):
        """
        Inserta los datos en la tabla de hechos.
        Adaptado para el dataset global (nuevas columnas).
        
        Args:
            df: DataFrame transformado
            mapeos: Diccionario con mapeos de IDs de dimensiones
            
        Returns:
            Número de registros insertados
        """
        self._log("\n📥 Insertando hechos (ofertas laborales)...")
        
        registros_insertados = 0
        errores = 0
        
        for idx, row in df.iterrows():
            try:
                # Obtener IDs de dimensiones
                tecnologia = row.get('tecnologia_principal', 'No especificada')
                tecnologia_id = mapeos['tecnologia'].get(tecnologia)
                
                empresa = row.get('company', None)
                empresa_id = mapeos['empresa'].get(empresa) if empresa else None
                
                # Usar country como ubicación principal
                ubicacion = row.get('country', row.get('location', None))
                ubicacion_id = mapeos['ubicacion'].get(ubicacion) if ubicacion else None
                
                seniority = row.get('seniority_name', row.get('seniority', 'No especificado'))
                seniority_id = self.obtener_seniority_id(seniority)
                
                # Obtener salario (priorizar salary_usd, luego base_salary_usd)
                salario_usd = row.get('salary_usd', row.get('base_salary_usd', None))
                
                # Insertar oferta con todas las columnas del dataset global
                self.cursor.execute("""
                    INSERT INTO fact_oferta (
                        titulo, salario_usd, experiencia_requerida, skills, 
                        educacion_requerida, fuente, tecnologia_id, seniority_id, 
                        empresa_id, ubicacion_id, survey_year, job_category,
                        annual_bonus_usd, total_compensation_usd, job_satisfaction,
                        gender, work_setting, ai_adoption_level, years_at_company
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    row.get('job_title'),
                    salario_usd,
                    row.get('experience_level', row.get('experience_required')),
                    row.get('primary_skills', row.get('skills')),
                    row.get('education_level'),
                    'global_ai_tech_salaries_2020_2025',
                    tecnologia_id,
                    seniority_id,
                    empresa_id,
                    ubicacion_id,
                    row.get('survey_year'),
                    row.get('job_category'),
                    row.get('annual_bonus_usd'),
                    row.get('total_compensation_usd'),
                    row.get('job_satisfaction'),
                    row.get('gender'),
                    row.get('work_setting'),
                    row.get('ai_adoption_level'),
                    row.get('years_at_company')
                ))
                registros_insertados += 1
                
                if registros_insertados % 100 == 0:
                    self._log(f"   ... {registros_insertados} registros insertados")
                    
            except Exception as e:
                errores += 1
                if errores <= 5:  # Mostrar solo los primeros 5 errores
                    self._log(f"   ⚠️ Error en registro {idx}: {e}")
        
        self.connection.commit()
        self._log(f"\n   ✅ Resumen de carga:")
        self._log(f"      - Registros insertados: {registros_insertados}")
        self._log(f"      - Errores: {errores}")
        
        return registros_insertados
    
    def cargar_dataset(self, df):
        """
        Carga el dataset completo a la base de datos.
        
        Args:
            df: DataFrame transformado
            
        Returns:
            Diccionario con estadísticas de carga
        """
        self._log("\n" + "=" * 60)
        self._log("💾 INICIANDO CARGA A BASE DE DATOS")
        self._log("=" * 60)
        
        # 1. Conectar
        if not self.conectar():
            return {'error': 'No se pudo conectar a la base de datos'}
        
        # 2. Crear tablas
        if not self.crear_tablas():
            return {'error': 'No se pudieron crear las tablas'}
        
        # 3. Insertar dimensiones
        mapeos = self.insertar_dimensiones(df)
        
        # 4. Insertar hechos
        registros = self.insertar_hechos(df, mapeos)
        
        # 5. Cerrar conexión
        self.cerrar()
        
        return {
            'registros_procesados': len(df),
            'registros_insertados': registros,
            'tecnologias_insertadas': len(mapeos['tecnologia']),
            'empresas_insertadas': len(mapeos['empresa']),
            'ubicaciones_insertadas': len(mapeos['ubicacion'])
        }
    
    def cerrar(self):
        """Cierra la conexión a la base de datos."""
        if self.connection:
            self.connection.close()
            self._log("\n🔌 Conexión cerrada")
    
    def obtener_logs(self):
        """Retorna los logs del proceso."""
        return self.logs


# ============================================================
# FUNCIÓN DE PRUEBA
# ============================================================

def probar_carga(df):
    """
    Función de prueba para el módulo de carga.
    
    Args:
        df: DataFrame transformado
        
    Returns:
        True si la carga fue exitosa, False en caso contrario
    """
    print("\n" + "=" * 60)
    print("🧪 PRUEBA DEL MÓDULO DE CARGA")
    print("=" * 60)
    
    loader = DatabaseLoader()
    resultado = loader.cargar_dataset(df)
    
    if 'error' in resultado:
        print(f"\n❌ Error en la carga: {resultado['error']}")
        return False
    
    print(f"\n✅ Carga exitosa:")
    print(f"   - Registros procesados: {resultado['registros_procesados']}")
    print(f"   - Registros insertados: {resultado['registros_insertados']}")
    print(f"   - Tecnologías únicas: {resultado['tecnologias_insertadas']}")
    print(f"   - Empresas únicas: {resultado['empresas_insertadas']}")
    print(f"   - Ubicaciones únicas: {resultado['ubicaciones_insertadas']}")
    
    return True


if __name__ == "__main__":
    print("Este módulo debe ser importado, no ejecutado directamente.")
    print("Usa probar_carga(df) desde otro script.")