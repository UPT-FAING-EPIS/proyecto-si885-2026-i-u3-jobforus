"""
Prueba integrada del pipeline completo con el nuevo dataset global
JobForUs - Sistema de Inteligencia de Mercado Laboral

Este script ejecuta:
1. Extracción del dataset global
2. Transformación (con opción de filtro LATAM)
3. Carga a la base de datos SQLite
4. Verificación de resultados
"""

import sys
import os
import pandas as pd
import sqlite3

# Agregar la carpeta raíz del proyecto al path
proyecto_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(proyecto_root)

from src.extract.github_jobs_extractor import LocalJobsExtractor
from src.transform.global_dataset_transformer import GlobalDatasetTransformer
from src.load.database_loader import DatabaseLoader


def print_seccion(titulo, caracter="=", longitud=70):
    """Imprime una sección formateada."""
    print("\n" + caracter * longitud)
    print(f" {titulo}")
    print(caracter * longitud)


def mostrar_columnas(df, titulo="Columnas disponibles"):
    """Muestra las columnas de un DataFrame."""
    print(f"\n📋 {titulo}:")
    for col in df.columns:
        print(f"   - {col}")


def test_pipeline_completo(aplicar_filtro_latam=False, guardar_resultado=False):
    """
    Ejecuta el pipeline completo: Extracción -> Transformación -> Carga
    
    Args:
        aplicar_filtro_latam: Si es True, filtra solo países LATAM
        guardar_resultado: Si es True, guarda el dataset transformado en CSV
        
    Returns:
        True si todo fue exitoso, False en caso contrario
    """
    
    print_seccion("🚀 JOBFORUS - PIPELINE COMPLETO", "=", 70)
    
    # ============================================================
    # PASO 1: EXTRACCIÓN DE DATOS
    # ============================================================
    print_seccion("📥 PASO 1: EXTRACCIÓN DE DATOS", "-", 70)
    
    try:
        extractor = LocalJobsExtractor()
        df_original = extractor.extraer_dataset()
        
        if df_original is None:
            print("❌ Error: No se pudo extraer el dataset")
            return False
        
        print(f"\n✅ Extracción exitosa:")
        print(f"   - Registros: {len(df_original)}")
        print(f"   - Columnas: {len(df_original.columns)}")
        
        mostrar_columnas(df_original, "Primeras 10 columnas del dataset original")
        
    except Exception as e:
        print(f"❌ Error en extracción: {e}")
        return False
    
    # ============================================================
    # PASO 2: TRANSFORMACIÓN DE DATOS
    # ============================================================
    print_seccion("🔄 PASO 2: TRANSFORMACIÓN DE DATOS", "-", 70)
    
    if aplicar_filtro_latam:
        print(f"\n🌎 Aplicando filtro LATAM (países de Latinoamérica)")
    
    try:
        transformer = GlobalDatasetTransformer()
        df_transformado = transformer.transformar_completo(
            df_original, 
            aplicar_filtro_latam=aplicar_filtro_latam,
            guardar_resultado=guardar_resultado
        )
        
        if df_transformado is None or len(df_transformado) == 0:
            print("❌ Error: No se pudo transformar el dataset")
            return False
        
        print(f"\n✅ Transformación exitosa:")
        print(f"   - Registros originales: {len(df_original)}")
        print(f"   - Registros transformados: {len(df_transformado)}")
        print(f"   - Columnas finales: {len(df_transformado.columns)}")
        
        # Mostrar nuevas columnas agregadas
        nuevas_columnas = ['seniority_name', 'seniority_id', 'tecnologia_id', 
                          'ubicacion_id', 'work_setting_id', 'gender_id']
        columnas_presentes = [col for col in nuevas_columnas if col in df_transformado.columns]
        if columnas_presentes:
            print(f"\n   ✅ Nuevas columnas de ID agregadas:")
            for col in columnas_presentes:
                print(f"      - {col}")
        
    except Exception as e:
        print(f"❌ Error en transformación: {e}")
        return False
    
    # ============================================================
    # PASO 3: CARGA A BASE DE DATOS
    # ============================================================
    print_seccion("💾 PASO 3: CARGA A BASE DE DATOS", "-", 70)
    
    try:
        loader = DatabaseLoader()
        resultado_carga = loader.cargar_dataset(df_transformado)
        
        if 'error' in resultado_carga:
            print(f"❌ Error en carga: {resultado_carga['error']}")
            return False
        
        print(f"\n✅ Carga exitosa:")
        print(f"   - Registros procesados: {resultado_carga['registros_procesados']}")
        print(f"   - Registros insertados: {resultado_carga['registros_insertados']}")
        print(f"   - Tecnologías únicas: {resultado_carga['tecnologias_insertadas']}")
        print(f"   - Empresas únicas: {resultado_carga['empresas_insertadas']}")
        print(f"   - Ubicaciones únicas: {resultado_carga['ubicaciones_insertadas']}")
        
    except Exception as e:
        print(f"❌ Error en carga: {e}")
        return False
    
    # ============================================================
    # RESUMEN FINAL
    # ============================================================
    print_seccion("✅ PIPELINE COMPLETADO EXITOSAMENTE", "=", 70)
    print(f"\n📊 Resumen final:")
    print(f"   - Dataset original: {len(df_original)} registros")
    print(f"   - Dataset transformado: {len(df_transformado)} registros")
    print(f"   - Cargados a BD: {resultado_carga['registros_insertados']} registros")
    print(f"   - Tecnologías identificadas: {resultado_carga['tecnologias_insertadas']}")
    
    if aplicar_filtro_latam:
        print(f"\n🌎 Nota: Se aplicó filtro LATAM")
    
    return True


def test_solo_latam():
    """
    Ejecuta el pipeline completo con filtro LATAM
    """
    print_seccion("🌎 EJECUTANDO PIPELINE CON FILTRO LATAM", "=", 70)
    print("\nNota: Solo se incluirán países de Latinoamérica")
    
    return test_pipeline_completo(aplicar_filtro_latam=True, guardar_resultado=True)


def test_sin_filtro():
    """
    Ejecuta el pipeline completo sin filtro (datos globales)
    """
    return test_pipeline_completo(aplicar_filtro_latam=False, guardar_resultado=True)


def modo_automatico():
    """Ejecuta en modo automático para GitHub Actions"""
    print("🚀 Ejecutando pipeline en modo automático...")
    return test_sin_filtro()


if __name__ == "__main__":
    # Si se pasa el argumento --auto, ejecutar en modo automático
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        resultado = modo_automatico()
        sys.exit(0 if resultado else 1)
    else:
        # Modo interactivo original
        print("=" * 70)
        print("🧪 JOBFORUS - PRUEBA INTEGRADA DEL PIPELINE COMPLETO")
        print("=" * 70)
        print("\nSelecciona una opción:")
        print("   1. Ejecutar pipeline con DATOS GLOBALES (todos los países)")
        print("   2. Ejecutar pipeline con FILTRO LATAM (solo Latinoamérica)")
        print("   3. Ejecutar ambas pruebas")
        print("   4. Salir")
        
        opcion = input("\nIngresa tu opción (1-4): ").strip()
        
        if opcion == "1":
            test_sin_filtro()
        elif opcion == "2":
            test_solo_latam()
        elif opcion == "3":
            print("\n" + "=" * 70)
            print("📊 PRIMERA PRUEBA: DATOS GLOBALES")
            print("=" * 70)
            test_sin_filtro()
            
            print("\n" + "=" * 70)
            print("📊 SEGUNDA PRUEBA: FILTRO LATAM")
            print("=" * 70)
            test_solo_latam()
        else:
            print("Saliendo...")