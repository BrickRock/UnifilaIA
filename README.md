USUARIO Y CONTRASEÑA PARA LA PÁGINA DEL STAFF MÉDICO
USUARIO: admin
contraseña: admin13

================================================================================
  UNIFILA IA — RESUMEN TÉCNICO DEL SISTEMA
  Gestión inteligente de filas médicas con predicción por IA
================================================================================

DESCRIPCIÓN GENERAL
───────────────────
UnifilaIA es un sistema de gestión de filas para clínicas del IMSS que combina
priorización por factores de riesgo clínico, predicción de duración de consulta
mediante un modelo de Machine Learning (Random Forest), y un mecanismo de
resiliencia inspirado en el patrón Circuit Breaker para evitar que el sistema
acepte pacientes cuando la capacidad de atención está saturada.

El sistema tiene dos frontends diferenciados:
  - Hackaton/     → App del paciente (React + TypeScript, puerto 5173)
                    Registro, login con JWT, ingreso a la fila virtual,
                    seguimiento de posición y hora de arribo sugerida.
  - unifila-app/  → Panel del staff (React + JavaScript, puerto 5174)
                    Registro presencial de pacientes, gestión de la cola,
                    asignación a consultorios, visualización dinámica de
                    salas.

Ambos consumen el mismo backend FastAPI (puerto 8000) conectado a PostgreSQL.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. CIRCUIT BREAKER — RESILIENCIA ANTE SATURACIÓN
──────────────────────────────────────────────────
Archivo clave: utils.py, router/atencion.py

El sistema adapta el patrón Circuit Breaker para controlar el flujo de nuevos
pacientes a la fila virtual. Se definen tres estados:

  NORMAL       →  Sistema operando con capacidad disponible.
                  Acepta nuevos registros sin restricción.

  SATURANDOSE  →  Señal de alerta temprana. La cola está creciendo
                  por encima del umbral esperado. Punto de intervención
                  para que el staff tome decisiones preventivas.

  SATURADO     →  El sistema rechaza activamente nuevos ingresos.
                  POST /atencion/registrar devuelve HTTP 503.
                  Equivale al estado "OPEN" del circuit breaker clásico.

Decisión de diseño (demo): La estructura de estados y el guardián (503 en
SATURADO) están implementados. La lógica de transición automática entre estados
—por ejemplo, cambiar a SATURANDOSE cuando la cola supera N pacientes— es trabajo
futuro. En el prototipo actual el estado se gestiona manualmente, lo que permite
demostrar el mecanismo sin requerir datos de producción reales.

Esto evita el problema real que quería resolverse: personas formadas que
no van a ser atendidas porque el sistema ya no tiene capacidad.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. PREDICTOR DE DURACIÓN — RANDOM FOREST
──────────────────────────────────────────
Archivos clave: predictor.py, queue_engine.py

El corazón predictivo del sistema es un modelo RandomForestRegressor de
scikit-learn entrenado con datos históricos de consultas médicas (datos dummy).

  Entrenamiento (predictor.py):
    - Dataset: dataset_consultas.csv (consultas históricas)
    - Features (7): preventiva, mas_de_un_sintoma, adulto, comorbilidad,
                    tiene_laboratorio, es_seguimiento, num_consulta_turno
    - Target: duracion_minutos (continuo)
    - Hiperparámetros: 200 árboles, profundidad máxima 10, seed=42
    - Artefacto: modelo_consultas.joblib (cargado una sola vez en memoria)

  Inferencia en tiempo real (queue_engine.py → QueueEngine.predict_duracion):
    - Construye un DataFrame con los 7 features del paciente entrante
    - Llama al modelo serializado
    - Devuelve duración estimada en minutos
    - Si el modelo no está disponible (joblib ausente): devuelve None
      y el sistema usa fallback de 15 min/paciente (cold start)

  Uso de la predicción:
    1. El valor se guarda en TurnoSimplificado.duracion_estimada_minutos (BD)
    2. Al siguiente registro, se suma el total de duraciones previas:
         suma_anteriores = Σ(duracion_estimada_minutos en cola)
    3. La hora sugerida de arribo se calcula como:
         hora_arribo = ahora + max(0, suma_anteriores − 15 min)
       El buffer de 15 minutos absorbe imprevistos (cancelaciones, no-shows)
    4. Esta hora se devuelve al paciente para que llegue justo a tiempo,
       reduciendo el tiempo de espera en sala.

  Importancia del num_consulta_turno como feature:
    Captura la posición en la cola como variable predictora. Las consultas
    en las primeras posiciones del día tienden a tener patrones distintos
    a las del final de la jornada.

  Para reentrenar el modelo (dentro del contenedor Docker):
    docker exec <container> python predictor.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. MÓDULO DE FILA VIRTUAL (APP DEL PACIENTE)
─────────────────────────────────────────────
Archivos clave: router/atencion.py, models.py (TurnoSimplificado), schemas.py

El paciente se registra con 6 indicadores clínicos binarios (0/1):
  - preventiva          ¿Es consulta preventiva?
  - mas_de_un_sintoma   ¿Presenta más de un síntoma?
  - adulto              ¿Es adulto mayor (≥65)?
  - comorbilidad        ¿Tiene comorbilidades?
  - tiene_laboratorio   ¿Lleva resultados de laboratorio?
  - es_seguimiento      ¿Es consulta de seguimiento?

  Score de prioridad = suma de los 6 indicadores (0-6)
  Mayor score → mayor prioridad en la cola

  Orden de atención:
    Primario:    score DESC (más factores de riesgo = se atiende antes)
    Secundario:  id ASC    (mismo score → quien llegó primero)

  Garantías del módulo:
    - Un NSS solo puede tener un turno activo simultáneo (409 si intenta
      registrarse dos veces)
    - Al recargar la app, el sistema detecta automáticamente si el paciente
      ya tiene turno activo (GET /atencion/estado/{nss}) y lo lleva
      directamente a la pantalla de seguimiento
    - La pantalla de seguimiento muestra alertas visuales escalonadas:
        > 60 min  → Normal (verde)
        ≤ 60 min  → Alerta amarilla (preséntate pronto)
        ≤ 15 min  → Alerta roja pulsante (dirígete ahora)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. MÓDULO DE REGISTRO PRESENCIAL (PANEL DEL STAFF)
────────────────────────────────────────────────────
Archivos clave: router/pacientes.py, services.py, unifila-app/

La asistente médica usa unifila-app para registrar presencialmente a pacientes
que llegan sin cita previa. Este módulo opera sobre el modelo PacienteFormado
(no TurnoSimplificado), que incluye datos completos del paciente:

  - NSS, nombre completo, fecha de nacimiento, sexo, crónico
  - Tipo de consulta (PRIMERA_VEZ, SEGUIMIENTO, URGENCIA, PROCEDIMIENTO)
  - Consultorio asignado (opcional al registro, asignable después)
  - Estado de atención: estado máquina → EN_ESPERA → LLAMADO →
                         EN_ATENCION → FINALIZADO / CANCELADO / NO_PRESENTADO

  Por qué esto resuelve el problema de los intervalos:
    El staff registra los criterios clínicos con mayor criterio que el
    paciente auto-reportando en la app. Esto alimenta scores más precisos,
    lo que produce una cola más ordenada y hace que las predicciones de
    duración del RF sean más confiables, permitiendo dar intervalos de
    tiempo más exactos a los pacientes.

  Consultorios disponibles:
    GET /consultorios devuelve lista dinámica (seed: 101 P1, 102 P1, 201 P2)
    con campo "ocupado" calculado en tiempo real (cualquier PacienteFormado
    en estado EN_ATENCION ligado a ese consultorio).

  No-show TTL:
    QueueEngine.check_no_show_ttl() marca como NO_PRESENTADO a pacientes
    en estado LLAMADO que no se presentaron en los últimos 5 minutos.
    Esto libera el slot y recalcula la cola activa.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5. SISTEMA DE CITAS (DISEÑO IMPLEMENTADO, ROL PENDIENTE)
──────────────────────────────────────────────────────────
Archivos clave: router/consultas.py, models.py (Consulta), router/turnos.py

El sistema de citas existe y funciona a nivel de endpoints y base de datos.
La arquitectura fue diseñada con la siguiente intención:

  - Solo médico o asistente médica puede crear/cerrar consultas
  - Un subconjunto pequeño de consultorios se reserva para citas agendadas
    (el resto opera bajo la lógica de fila virtual)
  - Al registrar una consulta (POST /consultas), el turno asociado pasa
    automáticamente a FINALIZADO y se registra hora_fin_atencion

  Estado actual del prototipo:
    El módulo funciona técnicamente pero el guard de rol (verificar que
    quien llama tiene role=admin o role=medico en el JWT) no está
    implementado todavía. Esto está identificado como deuda técnica.

  Lo que sí está completo:
    - Registro de diagnóstico, duración real, hora inicio/fin, notas
    - Transición automática de estado al cerrar consulta
    - Cálculo de tiempo de espera real (hora_llamado - hora_llegada)
    - Cancelación con guardián de estado final (no se puede cancelar
      lo que ya está FINALIZADO o NO_PRESENTADO)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

6. AUTENTICACIÓN
─────────────────
Archivos clave: router/auth.py

JWT HS256 con expiración de 24 horas, generado con PyJWT.

  Flujos:
    Paciente  →  POST /auth/login { user: NSS, password: "admin" }
                 → Busca Paciente en BD por NSS → emite token con role=patient
    Admin     →  POST /auth/login { user: "admin", password: "admin" }
                 → Token con role=admin

  Payload JWT: { sub, nss, nombre, id, role, exp }

  El frontend almacena el token en localStorage y lo decodifica para
  restaurar la sesión al recargar (exp * 1000 > Date.now()).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

7. PATRONES DE DISEÑO APLICADOS
──────────────────────────────────
  Patrón              Dónde                        Para qué
  ──────────────────  ───────────────────────────  ─────────────────────────────
  Circuit Breaker     utils.py + atencion.py       Bloquear ingreso en saturación
  Singleton           database.py                  Pool único de conexión BD
  State Machine       models.py (EstadoAtencion)   Ciclo de vida del turno
  Cold Start          queue_engine.py              Fallback sin modelo ML
  TTL / No-show       queue_engine.py              Limpieza automática de cola
  Service Layer       services.py                  Lógica de negocio separada
  DTO / Schema        schemas.py                   Validación en frontera API
  Dependency Inj.     todos los routers            Sesión BD por request

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

8. STACK TECNOLÓGICO
─────────────────────
  Backend:    Python 3.12, FastAPI 0.136, SQLAlchemy 2.0, PostgreSQL (psycopg2)
  ML:         scikit-learn 1.5.2 (RandomForestRegressor), pandas, joblib
  Auth:       PyJWT 2.9.0
  Frontend 1: React 18 + TypeScript + Vite (pacientes)
  Frontend 2: React 19 + JavaScript + Vite (staff / unifila-app)
  Infra:      Docker (FastAPI + PostgreSQL en contenedores separados)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


