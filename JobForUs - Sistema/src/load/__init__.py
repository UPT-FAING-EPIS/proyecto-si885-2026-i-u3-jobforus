"""
Script de prueba del módulo de carga a base de datos
Ubicado en: tests/test_load.py
"""

import sys
import os

# Agregar la carpeta raíz del proyecto al path
proyecto_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(proyecto_root)

print(f"📁 Ruta del proyecto: {proyecto_root}")

from src.extract.github_jobs_extractor import LocalJobsExtractor
from src.transform import TransformadorCompleto
from src.load.database_loader import DatabaseLoader


def test_carga_completa():
    """
    Prueba el pipeline completo: Extracción -> Transformación -> Carga
    """
    print("=" * 60)
    print("🚀 JOBFORUS - PRUEBA DE CARGA COMPLETA")
    print("=" * 60)
    
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
    transformador = TransformadorCompleto()
    df_transformado = transformador.transformar(df_original)
    
    print(f"   ✅ Dataset transformado: {len(df_transformado)} registros")
    
    # Paso 3: Cargar a base de datos
    print("\n💾 PASO 3: Cargando a base de datos...")
    loader = DatabaseLoader()
    resultado = loader.cargar_dataset(df_transformado)
    
    if 'error' in resultado:
        print(f"❌ Error en la carga: {resultado['error']}")
        return False
    
    # Mostrar resultados
    print("\n" + "=" * 60)
    print("📊 RESULTADOS DE LA CARGA")
    print("=" * 60)
    print(f"   - Registros procesados: {resultado['registros_procesados']}")
    print(f"   - Registros insertados: {resultado['registros_insertados']}")
    print(f"   - Tecnologías únicas: {resultado['tecnologias_insertadas']}")
    print(f"   - Empresas únicas: {resultado['empresas_insertadas']}")
    print(f"   - Ubicaciones únicas: {resultado['ubicaciones_insertadas']}")
    
    return True


def test_verificar_base_datos():
    """
    Verifica que los datos se hayan cargado correctamente.
    """
    print("\n" + "=" * 60)
    print("🔍 VERIFICANDO BASE DE DATOS")
    print("=" * 60)
    
    loader = DatabaseLoader()
    
    if not loader.conectar():
        print("❌ No se pudo conectar a la base de datos")
        return False
    
    # Verificar tablas
    loader.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tablas = loader.cursor.fetchall()
    print(f"\n📋 Tablas creadas:")
    for tabla in tablas:
        print(f"   - {tabla[0]}")
    
    # Verificar registros en fact_oferta
    loader.cursor.execute("SELECT COUNT(*) FROM fact_oferta")
    ofertas_count = loader.cursor.fetchone()[0]
    print(f"\n📊 Registros en fact_oferta: {ofertas_count}")
    
    # Verificar dimensiones
    loader.cursor.execute("SELECT COUNT(*) FROM dim_tecnologia")
    tech_count = loader.cursor.fetchone()[0]
    print(f"   - Tecnologías: {tech_count}")
    
    loader.cursor.execute("SELECT COUNT(*) FROM dim_empresa")
    emp_count = loader.cursor.fetchone()[0]
    print(f"   - Empresas: {emp_count}")
    
    loader.cursor.execute("SELECT COUNT(*) FROM dim_ubicacion")
    ub_count = loader.cursor.fetchone()[0]
    print(f"   - Ubicaciones: {ub_count}")
    
    # Verificar vistas
    loader.cursor.execute("SELECT COUNT(*) FROM vw_salario_por_tecnologia")
    vistas = loader.cursor.fetchone()[0]
    print(f"\n📊 Vistas creadas correctamente")
    
    # Mostrar top 5 tecnologías
    print(f"\n🏆 Top 5 tecnologías más demandadas:")
    loader.cursor.execute("SELECT tecnologia, cantidad_ofertas FROM vw_tecnologias_demandadas LIMIT 5")
    top_tech = loader.cursor.fetchall()
    for tech, count in top_tech:
        print(f"   - {tech}: {count} ofertas")
    
    # Mostrar salarios por seniority
    print(f"\n💰 Salarios promedio por seniority:")
    loader.cursor.execute("SELECT seniority, salario_promedio FROM vw_salario_por_seniority")
    salarios = loader.cursor.fetchall()
    for seniority, salario in salarios:
        print(f"   - {seniority}: ${salario:,.0f}")
    
    loader.cerrar()
    
    return True


if __name__ == "__main__":
    # Ejecutar carga completa
    if test_carga_completa():
        test_verificar_base_datos()
    else:
        print("\n❌ La carga no se completó correctamente")