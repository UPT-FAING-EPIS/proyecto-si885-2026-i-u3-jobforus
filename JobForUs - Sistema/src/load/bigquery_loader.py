"""
Cargador a BigQuery para JobForUs
Carga la tabla de hechos y las tablas de dimensiones
"""

import pandas as pd
import sys
from google.cloud import bigquery
from google.oauth2 import service_account
from datetime import datetime
from pathlib import Path


class BigQueryLoader:
    def __init__(self):
        # Configuración del proyecto
        self.project_id = "jobforus-project"
        self.dataset_id = "job_market"
        self.table_id = "fact_oferta"
        self.client = None
    
    def conectar(self):
        """Conecta a BigQuery usando credenciales"""
        try:
            script_dir = Path(__file__).parent.parent.parent
            cred_path = script_dir / "credentials" / "gcp-key.json"
            
            print(f"🔍 Buscando credenciales en: {cred_path}")
            
            if cred_path.exists():
                credentials = service_account.Credentials.from_service_account_file(
                    str(cred_path)
                )
                self.client = bigquery.Client(
                    credentials=credentials,
                    project=self.project_id
                )
                print(f"✅ Conectado a BigQuery - Proyecto: {self.project_id}")
                return True
            else:
                print(f"❌ No se encontró el archivo: {cred_path}")
                return False
            
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return False
    
    def crear_dataset_si_no_existe(self):
        """Crea el dataset si no existe"""
        try:
            dataset_ref = f"{self.project_id}.{self.dataset_id}"
            self.client.get_dataset(dataset_ref)
            print(f"📁 Dataset {self.dataset_id} ya existe")
        except Exception:
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = "US"
            dataset.description = "Dataset JobForUs - Análisis de mercado laboral tecnológico"
            self.client.create_dataset(dataset)
            print(f"✅ Dataset {self.dataset_id} creado")
    
    def cargar_tabla(self, df, nombre_tabla, write_disposition="WRITE_TRUNCATE"):
        """
        Carga un DataFrame a una tabla de BigQuery
        
        Args:
            df: DataFrame a cargar
            nombre_tabla: Nombre de la tabla (ej: 'fact_oferta', 'dim_seniority')
            write_disposition: WRITE_TRUNCATE (sobrescribe) o WRITE_APPEND (agrega)
        """
        if df is None or len(df) == 0:
            print(f"   ⚠️ No hay datos para {nombre_tabla}")
            return False
        
        table_ref = f"{self.project_id}.{self.dataset_id}.{nombre_tabla}"
        
        job_config = bigquery.LoadJobConfig(
            write_disposition=write_disposition,
            autodetect=True
        )
        
        try:
            job = self.client.load_table_from_dataframe(
                df, table_ref, job_config=job_config
            )
            job.result()
            print(f"   ✅ {nombre_tabla}: {len(df)} registros")
            return True
        except Exception as e:
            print(f"   ❌ Error cargando {nombre_tabla}: {e}")
            return False
    
    def recargar_con_dimensiones_limpias(self, archivo_csv=None):
        """
        Recarga datos completos: hechos + dimensiones limpias
        """
        print("\n" + "=" * 60)
        print("🔄 RECARGANDO DATOS CON DIMENSIONES LIMPIAS")
        print("=" * 60)
        
        # 1. Conectar
        if not self.conectar():
            return False
        
        # 2. Borrar dataset si existe
        try:
            dataset_ref = f"{self.project_id}.{self.dataset_id}"
            self.client.delete_dataset(dataset_ref, delete_contents=True)
            print(f"🗑️ Dataset {self.dataset_id} eliminado")
        except Exception as e:
            print(f"📁 Dataset {self.dataset_id} no existía: {e}")
        
        # 3. Crear dataset nuevo
        self.crear_dataset_si_no_existe()
        
        # 4. Leer CSV transformado (con datos limpios)
        if archivo_csv is None:
            script_dir = Path(__file__).parent.parent.parent
            archivo_csv = script_dir / "data" / "processed" / "global_dataset_transformado.csv"
        
        if not Path(archivo_csv).exists():
            print(f"❌ Archivo no encontrado: {archivo_csv}")
            print(f"💡 Ejecuta primero: python tests/test_pipeline_completo.py")
            return False
        
        df = pd.read_csv(archivo_csv)
        print(f"📊 CSV leído: {len(df)} registros")
        print(f"📋 Columnas disponibles: {list(df.columns)}")
        
        # 5. Cargar tabla de hechos
        print("\n📥 CARGANDO TABLA DE HECHOS")
        df['fecha_carga'] = datetime.now()
        self.cargar_tabla(df, "fact_oferta", "WRITE_TRUNCATE")
        
        # 6. Cargar dimensiones (desde los datos limpios)
        print("\n📊 CARGANDO TABLAS DE DIMENSIONES")
        
        # dim_seniority
        if 'seniority_id' in df.columns and 'seniority_name' in df.columns:
            dim = df[['seniority_id', 'seniority_name']].drop_duplicates()
            dim = dim[dim['seniority_id'] > 0]
            dim = dim.rename(columns={'seniority_name': 'nivel'})
            self.cargar_tabla(dim, "dim_seniority", "WRITE_TRUNCATE")
            print(f"      - Niveles: {len(dim)}")
        
        # dim_ubicacion
        if 'ubicacion_id' in df.columns and 'country' in df.columns:
            dim = df[['ubicacion_id', 'country', 'continent']].drop_duplicates()
            dim = dim[dim['ubicacion_id'] > 0]
            dim = dim.rename(columns={'country': 'pais'})
            self.cargar_tabla(dim, "dim_ubicacion", "WRITE_TRUNCATE")
            print(f"      - Países: {len(dim)}")
        
        # dim_work_setting
        if 'work_setting_id' in df.columns and 'work_setting' in df.columns:
            dim = df[['work_setting_id', 'work_setting']].drop_duplicates()
            dim = dim[dim['work_setting_id'] > 0]
            dim = dim.rename(columns={'work_setting': 'nombre'})
            self.cargar_tabla(dim, "dim_work_setting", "WRITE_TRUNCATE")
            print(f"      - Modalidades: {len(dim)}")
        
        # dim_gender
        if 'gender_id' in df.columns and 'gender' in df.columns:
            dim = df[['gender_id', 'gender']].drop_duplicates()
            dim = dim[dim['gender_id'] > 0]
            dim = dim.rename(columns={'gender': 'nombre'})
            self.cargar_tabla(dim, "dim_gender", "WRITE_TRUNCATE")
            print(f"      - Géneros: {len(dim)}")
        
        # dim_tecnologia (CON VALORES LIMPIOS)
        if 'tecnologia_id' in df.columns and 'tecnologia_principal' in df.columns:
            dim = df[['tecnologia_id', 'tecnologia_principal', 'categoria_principal']].drop_duplicates()
            dim = dim[dim['tecnologia_id'] > 0]
            dim = dim.rename(columns={
                'tecnologia_principal': 'nombre',
                'categoria_principal': 'categoria'
            })
            # Limpiar valores que contengan múltiples tecnologías
            dim = dim[~dim['nombre'].str.contains(';', na=False)]
            dim = dim[~dim['nombre'].str.contains(',', na=False)]
            dim = dim.head(1000)
            self.cargar_tabla(dim, "dim_tecnologia", "WRITE_TRUNCATE")
            print(f"      - Tecnologías limpias: {len(dim)}")
        
        print("\n" + "=" * 60)
        print("✅ RECARGA COMPLETADA EXITOSAMENTE")
        print(f"   - Tabla de hechos: fact_oferta ({len(df)} registros)")
        print("   - Dimensiones cargadas: dim_seniority, dim_ubicacion, dim_work_setting, dim_gender, dim_tecnologia")
        print("=" * 60)
        
        return True
    
    def cargar_desde_csv_simple(self, archivo_csv=None):
        """
        Versión simple: solo carga la tabla de hechos (sin dimensiones)
        """
        try:
            if archivo_csv is None:
                script_dir = Path(__file__).parent.parent.parent
                archivo_csv = script_dir / "data" / "processed" / "global_dataset_transformado.csv"
            
            print(f"📁 Leyendo archivo: {archivo_csv}")
            
            if not Path(archivo_csv).exists():
                print(f"❌ Archivo no encontrado: {archivo_csv}")
                return False
            
            df = pd.read_csv(archivo_csv)
            print(f"📊 CSV leído: {len(df)} registros")
            
            df['fecha_carga'] = datetime.now()
            
            return self.cargar_tabla(df, "fact_oferta", "WRITE_TRUNCATE")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False


def modo_automatico():
    """Ejecuta en modo automático para GitHub Actions"""
    print("🚀 Ejecutando en modo automático...")
    loader = BigQueryLoader()
    loader.recargar_con_dimensiones_limpias()
    return True


if __name__ == "__main__":
    # Si se pasa el argumento --auto, ejecutar en modo automático
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        modo_automatico()
    else:
        # Modo interactivo original
        print("=" * 60)
        print("CARGADOR A BIGQUERY - JOBFORUS")
        print("=" * 60)
        print("\nOpciones:")
        print("   1. Recargar datos completos (con dimensiones limpias)")
        print("   2. Solo cargar tabla de hechos")
        print("   3. Salir")
        
        opcion = input("\nIngresa tu opción (1-3): ").strip()
        
        if opcion == "1":
            loader = BigQueryLoader()
            loader.recargar_con_dimensiones_limpias()
        elif opcion == "2":
            loader = BigQueryLoader()
            loader.cargar_desde_csv_simple()
        else:
            print("Saliendo...")