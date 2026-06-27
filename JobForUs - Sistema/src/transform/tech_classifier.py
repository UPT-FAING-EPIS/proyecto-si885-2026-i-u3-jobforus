"""
Módulo de clasificación de tecnologías (versión original)
JobForUs - Sistema de Inteligencia de Mercado Laboral
"""

import pandas as pd


class TechClassifier:
    """
    Clase encargada de clasificar las tecnologías.
    (Versión original - mantiene compatibilidad)
    """
    
    def __init__(self):
        self.logs = []
        
        self.tech_categories = {
            'Backend': ['Python', 'Java', 'Go', 'Node.js', 'Ruby', 'C#', '.NET', 'PHP'],
            'Frontend': ['React', 'Angular', 'Vue', 'JavaScript', 'TypeScript', 'HTML', 'CSS'],
            'Database': ['SQL', 'PostgreSQL', 'MySQL', 'MongoDB', 'Oracle', 'Redis'],
            'Cloud': ['AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes'],
            'DevOps': ['DevOps', 'CI/CD', 'Jenkins', 'Terraform', 'Ansible', 'Git'],
            'Data': ['Machine Learning', 'Data Science', 'AI', 'TensorFlow', 'Pandas', 'NumPy', 'Spark', 'Hadoop']
        }
    
    def _log(self, message):
        self.logs.append(message)
        print(f"   {message}")
    
    def clasificar_tecnologia_principal(self, skills_texto):
        if pd.isna(skills_texto) or skills_texto == '':
            return 'Sin tecnología'
        
        skills_texto = str(skills_texto).lower()
        
        for categoria, tecnologias in self.tech_categories.items():
            for tech in tecnologias:
                if tech.lower() in skills_texto:
                    return tech
        
        return 'Otra'
    
    def clasificar_categoria_principal(self, skills_texto):
        if pd.isna(skills_texto) or skills_texto == '':
            return 'No especificada'
        
        skills_texto = str(skills_texto).lower()
        
        for categoria, tecnologias in self.tech_categories.items():
            for tech in tecnologias:
                if tech.lower() in skills_texto:
                    return categoria
        
        return 'Otra'
    
    def clasificar_dataset(self, df):
        """Clasifica todo el dataset agregando columnas de tecnologías."""
        self._log("🔧 Clasificando tecnologías...")
        
        df_clasificado = df.copy()
        
        # Buscar columna de skills
        skills_col = None
        for col in ['primary_skills', 'skills', 'tech_skills']:
            if col in df_clasificado.columns:
                skills_col = col
                break
        
        if skills_col:
            df_clasificado['tecnologia_principal'] = df_clasificado[skills_col].apply(
                self.clasificar_tecnologia_principal
            )
            df_clasificado['categoria_principal'] = df_clasificado[skills_col].apply(
                self.clasificar_categoria_principal
            )
            
            top_tech = df_clasificado['tecnologia_principal'].value_counts().head(10)
            self._log(f"\n   📊 Top 10 tecnologías:")
            for tech, count in top_tech.items():
                if tech != 'Sin tecnología':
                    self._log(f"      - {tech}: {count} registros")
        else:
            self._log("   ⚠️ No se encontró columna de skills")
            df_clasificado['tecnologia_principal'] = 'No disponible'
            df_clasificado['categoria_principal'] = 'No disponible'
        
        return df_clasificado
    
    def obtener_logs(self):
        return self.logs