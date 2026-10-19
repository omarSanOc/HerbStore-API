---
name: sdd
description: Úsala siempre al crear, revisar, planificar, implementar, validar o cambiar docs/constitution.md o cualquier spec de HerbStore API.
---

# Spec-Driven Development (SDD)

## Flujo y aprobaciones

Constitución → Spec → Clarificación → Aprobación de spec → Plan → Tareas → Aprobación técnica → Implementación → Validación → Cambio.

- Nunca avances tras una puerta de aprobación sin un sí explícito del usuario.
- La spec manda: nada fuera de sus RF se implementa. Una duda de producto detiene el flujo; no se resuelve por suposición.
- Un requisito nuevo modifica primero spec, luego plan/tareas y finalmente código.
- Cada spec vive en `specs/NNN-nombre/` con `spec.md`, `plan.md` y `tasks.md`.
- Al cerrar cada fase, el agente con permiso actualiza `MEMORY.md` sin superar unas 50 líneas.

## Spec (`spec.md`)

```markdown
# Spec NNN — <Nombre>
Estado: borrador | aprobada | implementada
## Contexto y objetivo
## Usuarios
## Historias de usuario
- HU-1. Como <rol>, quiero <acción> para <beneficio>.
## Definiciones
## Requisitos funcionales
- RF-1: CUANDO <evento>, EL SISTEMA <respuesta verificable>.
## Requisitos no funcionales
## Casos límite
## Fuera de alcance
## Criterios de finalización
## Dudas abiertas
- [NECESITA ACLARACIÓN] <duda>
```

- Escribe requisitos EARS en español: `CUANDO`, `SI/ENTONCES`, `MIENTRAS` o comportamiento permanente.
- La spec contiene QUÉ y POR QUÉ, nunca stack, clases, tablas, endpoints internos ni nombres de archivo.
- Cada RF debe ser observable y medible; evita “rápido”, “seguro” o “correcto” sin criterio.

## Plan (`plan.md`)

Para cada RF especifica solo lo necesario:

- Archivos y responsabilidades respetando routes delgadas y lógica separada.
- Flujo HTTP y de datos; contrato JSON/OpenAPI y compatibilidad móvil.
- Lógica aislable; para tiempo usa reloj o `now` explícito.
- Persistencia, migraciones Alembic, transacciones, locks e idempotencia cuando apliquen.
- Errores, privacidad, `Accept-Language` e impacto en `en`/`es`.
- Pseudocódigo de algoritmos no triviales.
- Decisiones justificadas con alternativa descartada.
- Estrategia de Pytest: unidad/contrato con SQLite y PostgreSQL desechable para concurrencia o semántica propia del motor.
- Trazabilidad: indica los RF cubiertos por cada parte.

No agregues repositorios, servicios o abstracciones sin responsabilidad real.

## Tareas (`tasks.md`)

```markdown
- [ ] **T1. <Descripción>.** RF-1, RF-2
  - Hecho cuando: <comprobación verificable>.
```

- Orden de dependencia, 20–30 minutos por tarea y máximo diez; si excede, propone dividir la spec.
- Incluye por separado pruebas, migraciones y documentación solo cuando produzcan una comprobación útil.

## Implementación

Ejecuta una sola tarea y detente:

1. Lee constitución, AGENTS, MEMORY, spec, plan y tarea.
2. Escribe primero la prueba enfocada y confirma el fallo esperado.
3. Implementa únicamente lo requerido para ponerla en verde.
4. Ejecuta la prueba enfocada, `uv run ruff format --check .`, `uv run ruff check .` y `uv run pytest`.
5. Si afecta órdenes, inventario, locks o idempotencia, prueba también con PostgreSQL desechable.
6. Si cambia el esquema, valida Alembic upgrade/downgrade y el seed en una base desechable.
7. Marca solo esa tarea, actualiza `MEMORY.md` y para.

## Validación

- Recorre cada RF y enlázalo con evidencia concreta: test, status/payload HTTP, OpenAPI o migración.
- Verifica criterios de finalización, constitución, privacidad, i18n y ausencia de alcance extra.
- El reviewer no corrige: emite `APROBADO` o hallazgos bloqueantes con archivo/línea y RF/principio.
