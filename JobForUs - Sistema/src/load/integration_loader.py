"""
Script de integración para cargar datos transformados a BigQuery
Ejecuta el pipeline completo y sube los datos a la nube
"""

import sys
import os
import pandas as pd

# Agregar ruta del proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extract.github_jobs_extractor import LocalJobsExtractor
from transform.global_dataset_transformer import GlobalDatasetTransformer
from load.bigquery_loader import BigQueryLoader


def cargar_a_almacen(aplicar_filtro_latam=False):
    """
    Ejecuta el pipeline completo y carga los datos a BigQuery.
    
    Args:
        aplicar_filtro_latam: Si es True, filtra solo países LATAM
    """
    print("=" * 70)
    print("🚀 JOBFORUS - PIPELINE COMPLETO CON CARGA A BIGQUERY")
    print("=" * 70)
    
    # Paso 1: Extraer datos
    print("\n📥 PASO 1: Extrayendo datos...")
    extractor = LocalJobsExtractor()
    df_original = extractor.extraer_dataset()
    
    if df_original is None:
        print("❌ No se pudo extraer el dataset")
        return False
    
    print(f"   ✅ Dataset extraído: {len(df_original)} registros")
    
    # Paso 2: Transformar datos
    print("\n🔄 PASO 2: Transformando datos...")
    transformer = GlobalDatasetTransformer()
    df_transformado = transformer.transformar_completo(df_original, aplicar_filtro_latam)
    
    if df_transformado is None or len(df_transformado) == 0:
        print("❌ No se pudo transformar el dataset")
        return False
    
    print(f"   ✅ Dataset transformado: {len(df_transformado)} registros")
    
    # Paso 3: Cargar a BigQuery
    print("\n💾 PASO 3: Cargando a BigQuery...")
    loader = BigQueryLoader()
    resultado = loader.cargar_dataset_completo(df_transformado)
    
    if 'error' in resultado:
        print(f"❌ Error en carga: {resultado['error']}")
        return False
    
    print(f"\n✅ Proceso completado exitosamente")
    print(f"   - Registros cargados: {resultado['registros_cargados']}")
    print(f"   - Dataset: {resultado['dataset']}")
    print(f"   - Proyecto: {resultado['proyecto']}")
    
    return True


if __name__ == "__main__":
    print("Selecciona una opción:")
    print("   1. Cargar todos los datos (globales)")
    print("   2. Cargar solo datos LATAM")
    
    opcion = input("\nOpción (1-2): ").strip()
    
    if opcion == "2":
        cargar_a_almacen(aplicar_filtro_latam=True)
    else:
        cargar_a_almacen(aplicar_filtro_latam=False)