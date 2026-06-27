-- ============================================
-- ESQUEMA DE BASE DE DATOS - JOBFORUS
-- Modelo Estrella para análisis de mercado laboral
-- Versión 2.0 - Adaptado para dataset global
-- ============================================

-- ============================================
-- ELIMINAR TABLAS SI EXISTEN (para limpiar)
-- ============================================
DROP TABLE IF EXISTS fact_oferta;
DROP TABLE IF EXISTS dim_tecnologia;
DROP TABLE IF EXISTS dim_seniority;
DROP TABLE IF EXISTS dim_empresa;
DROP TABLE IF EXISTS dim_ubicacion;

-- ============================================
-- TABLAS DE DIMENSIONES
-- ============================================

-- 1. Dimensión: Tecnología
CREATE TABLE dim_tecnologia (
    tecnologia_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    categoria VARCHAR(30) NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Dimensión: Seniority (nivel de experiencia)
CREATE TABLE dim_seniority (
    seniority_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nivel VARCHAR(20) NOT NULL UNIQUE,
    años_min INTEGER,
    años_max INTEGER,
    descripcion TEXT
);

-- 3. Dimensión: Empresa
CREATE TABLE dim_empresa (
    empresa_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    tamano VARCHAR(50),
    industria VARCHAR(50),
    pais_origen VARCHAR(50),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Dimensión: Ubicación
CREATE TABLE dim_ubicacion (
    ubicacion_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ciudad VARCHAR(50),
    pais VARCHAR(50),
    continente VARCHAR(50),
    remoto BOOLEAN DEFAULT 0,
    nombre_completo VARCHAR(100)
);

-- ============================================
-- TABLA DE HECHOS (OFERTAS LABORALES)
-- Versión 2.0 - Adaptada para dataset global
-- ============================================
CREATE TABLE fact_oferta (
    oferta_id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Datos básicos de la oferta
    titulo VARCHAR(200) NOT NULL,
    job_category VARCHAR(50),
    skills TEXT,
    educacion_requerida VARCHAR(50),
    
    -- Datos salariales
    salario_usd DECIMAL(10,2),
    annual_bonus_usd DECIMAL(10,2),
    total_compensation_usd DECIMAL(10,2),
    
    -- Datos de experiencia
    experiencia_requerida VARCHAR(50),
    years_at_company INTEGER,
    
    -- Datos del entorno laboral
    work_setting VARCHAR(20),  -- Remote, Hybrid, On-site
    employment_type VARCHAR(20), -- Full-time, Freelance, Contract
    
    -- Datos demográficos
    gender VARCHAR(20),
    
    -- Tendencias
    ai_adoption_level VARCHAR(20), -- None, Partial, Experimenting, Significant, AI-First
    job_satisfaction DECIMAL(3,1), -- Escala 0-5
    
    -- Datos temporales
    survey_year INTEGER,
    fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Metadatos
    fuente VARCHAR(50),
    
    -- Claves foráneas
    tecnologia_id INTEGER,
    seniority_id INTEGER,
    empresa_id INTEGER,
    ubicacion_id INTEGER,
    
    -- Restricciones de integridad referencial
    FOREIGN KEY (tecnologia_id) REFERENCES dim_tecnologia(tecnologia_id),
    FOREIGN KEY (seniority_id) REFERENCES dim_seniority(seniority_id),
    FOREIGN KEY (empresa_id) REFERENCES dim_empresa(empresa_id),
    FOREIGN KEY (ubicacion_id) REFERENCES dim_ubicacion(ubicacion_id)
);

-- ============================================
-- ÍNDICES PARA MEJORAR EL RENDIMIENTO
-- ============================================

-- Índices para consultas comunes
CREATE INDEX idx_oferta_salario ON fact_oferta(salario_usd);
CREATE INDEX idx_oferta_anio ON fact_oferta(survey_year);
CREATE INDEX idx_oferta_tecnologia ON fact_oferta(tecnologia_id);
CREATE INDEX idx_oferta_seniority ON fact_oferta(seniority_id);
CREATE INDEX idx_oferta_empresa ON fact_oferta(empresa_id);
CREATE INDEX idx_oferta_ubicacion ON fact_oferta(ubicacion_id);

-- Índices para filtros comunes
CREATE INDEX idx_oferta_gender ON fact_oferta(gender);
CREATE INDEX idx_oferta_work_setting ON fact_oferta(work_setting);
CREATE INDEX idx_oferta_ai_adoption ON fact_oferta(ai_adoption_level);
CREATE INDEX idx_oferta_job_category ON fact_oferta(job_category);

-- Índice compuesto para consultas complejas
CREATE INDEX idx_oferta_tecnologia_seniority ON fact_oferta(tecnologia_id, seniority_id);
CREATE INDEX idx_oferta_anio_pais ON fact_oferta(survey_year, ubicacion_id);

-- ============================================
-- VISTAS PARA ANÁLISIS COMUNES
-- ============================================

-- Vista 1: Salarios por tecnología
CREATE VIEW vw_salario_por_tecnologia AS
SELECT 
    t.nombre AS tecnologia,
    t.categoria,
    COUNT(o.oferta_id) AS cantidad_ofertas,
    ROUND(AVG(o.salario_usd), 2) AS salario_promedio,
    ROUND(MIN(o.salario_usd), 2) AS salario_minimo,
    ROUND(MAX(o.salario_usd), 2) AS salario_maximo
FROM fact_oferta o
JOIN dim_tecnologia t ON o.tecnologia_id = t.tecnologia_id
WHERE o.salario_usd IS NOT NULL
GROUP BY t.nombre, t.categoria
ORDER BY cantidad_ofertas DESC;

-- Vista 2: Salarios por seniority
CREATE VIEW vw_salario_por_seniority AS
SELECT 
    s.nivel AS seniority,
    COUNT(o.oferta_id) AS cantidad_ofertas,
    ROUND(AVG(o.salario_usd), 2) AS salario_promedio,
    ROUND(MIN(o.salario_usd), 2) AS salario_minimo,
    ROUND(MAX(o.salario_usd), 2) AS salario_maximo,
    ROUND(AVG(o.annual_bonus_usd), 2) AS bono_promedio
FROM fact_oferta o
JOIN dim_seniority s ON o.seniority_id = s.seniority_id
WHERE o.salario_usd IS NOT NULL
GROUP BY s.nivel
ORDER BY s.seniority_id;

-- Vista 3: Tecnologías más demandadas
CREATE VIEW vw_tecnologias_demandadas AS
SELECT 
    t.nombre AS tecnologia,
    t.categoria,
    COUNT(o.oferta_id) AS cantidad_ofertas,
    ROUND(COUNT(o.oferta_id) * 100.0 / (SELECT COUNT(*) FROM fact_oferta), 2) AS porcentaje
FROM fact_oferta o
JOIN dim_tecnologia t ON o.tecnologia_id = t.tecnologia_id
GROUP BY t.nombre, t.categoria
ORDER BY cantidad_ofertas DESC;

-- Vista 4: Salarios por género (NUEVA)
CREATE VIEW vw_salario_por_genero AS
SELECT 
    o.gender,
    COUNT(o.oferta_id) AS cantidad_ofertas,
    ROUND(AVG(o.salario_usd), 2) AS salario_promedio,
    ROUND(AVG(o.total_compensation_usd), 2) AS compensacion_promedio,
    ROUND(AVG(o.job_satisfaction), 2) AS satisfaccion_promedio
FROM fact_oferta o
WHERE o.gender IS NOT NULL AND o.gender != ''
GROUP BY o.gender;

-- Vista 5: Salarios por modalidad de trabajo (NUEVA)
CREATE VIEW vw_salario_por_work_setting AS
SELECT 
    o.work_setting,
    COUNT(o.oferta_id) AS cantidad_ofertas,
    ROUND(AVG(o.salario_usd), 2) AS salario_promedio,
    ROUND(AVG(o.job_satisfaction), 2) AS satisfaccion_promedio
FROM fact_oferta o
WHERE o.work_setting IS NOT NULL
GROUP BY o.work_setting;

-- Vista 6: Evolución salarial por año (NUEVA)
CREATE VIEW vw_evolucion_salarial AS
SELECT 
    o.survey_year,
    COUNT(o.oferta_id) AS cantidad_ofertas,
    ROUND(AVG(o.salario_usd), 2) AS salario_promedio,
    ROUND(AVG(o.annual_bonus_usd), 2) AS bono_promedio,
    ROUND(AVG(o.total_compensation_usd), 2) AS compensacion_promedio
FROM fact_oferta o
WHERE o.survey_year IS NOT NULL
GROUP BY o.survey_year
ORDER BY o.survey_year;

-- Vista 7: Adopción de IA por año (NUEVA)
CREATE VIEW vw_adopcion_ia_por_anio AS
SELECT 
    o.survey_year,
    o.ai_adoption_level,
    COUNT(o.oferta_id) AS cantidad_ofertas,
    ROUND(COUNT(o.oferta_id) * 100.0 / SUM(COUNT(o.oferta_id)) OVER (PARTITION BY o.survey_year), 2) AS porcentaje
FROM fact_oferta o
WHERE o.ai_adoption_level IS NOT NULL
GROUP BY o.survey_year, o.ai_adoption_level
ORDER BY o.survey_year, o.ai_adoption_level;

-- Vista 8: Satisfacción laboral por seniority (NUEVA)
CREATE VIEW vw_satisfaccion_por_seniority AS
SELECT 
    s.nivel AS seniority,
    ROUND(AVG(o.job_satisfaction), 2) AS satisfaccion_promedio,
    COUNT(o.oferta_id) AS cantidad_ofertas
FROM fact_oferta o
JOIN dim_seniority s ON o.seniority_id = s.seniority_id
WHERE o.job_satisfaction IS NOT NULL
GROUP BY s.nivel
ORDER BY s.seniority_id;

-- ============================================
-- DATOS POR DEFECTO (SENIORITY)
-- ============================================
INSERT OR IGNORE INTO dim_seniority (nivel, años_min, años_max, descripcion) VALUES 
('Junior', 0, 2, 'Profesional con 0-2 años de experiencia'),
('Mid', 3, 5, 'Profesional con 3-5 años de experiencia'),
('Senior', 6, 9, 'Profesional con 6-9 años de experiencia'),
('Lead', 10, 99, 'Profesional con 10+ años de experiencia o liderazgo'),
('No especificado', NULL, NULL, 'No se especificó la experiencia requerida');

-- ============================================
-- CONSULTAS DE VERIFICACIÓN (opcionales)
-- ============================================

-- Verificar tablas creadas
-- SELECT name FROM sqlite_master WHERE type='table';

-- Verificar vistas creadas
-- SELECT name FROM sqlite_master WHERE type='view';

-- Verificar cantidad de registros por vista
-- SELECT 'vw_salario_por_tecnologia' as vista, COUNT(*) as registros FROM vw_salario_por_tecnologia
-- UNION ALL
-- SELECT 'vw_salario_por_seniority', COUNT(*) FROM vw_salario_por_seniority
-- UNION ALL
-- SELECT 'vw_tecnologias_demandadas', COUNT(*) FROM vw_tecnologias_demandadas;