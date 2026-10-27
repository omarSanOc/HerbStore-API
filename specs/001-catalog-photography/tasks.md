# Tareas 001

Las tareas documentan la entrega completa de 607 imágenes y su validación. Cada tarea está dimensionada para 20–30 minutos y no autoriza cambios fuera de la spec.

- [x] **T1. Contrastar el catálogo completo y fijar el inventario.** RF-1, RF-2
  - Hecho cuando: el manifiesto registra 300 productos y 607 assets; cada producto tiene frontal y detalle; categorías, banners, URLs, hashes y las 59 entradas originales coinciden.
- [x] **T2. Revisar y publicar los lotes restantes de productos.** RF-2, RF-3
  - Hecho cuando: los 274 productos ampliados tienen 548 PNG revisados, cada par conserva el mismo envase y no queda `pending`.
- [x] **T3. Verificar categorías, banners, proporciones y hashes.** RF-2, RF-3
  - Hecho cuando: existen cinco categorías y dos banners revisados, las proporciones cumplen su tipo y todos los SHA-256 coinciden.
- [x] **T4. Verificar resolución, fallback y nombres inválidos.** RF-4
  - Hecho cuando: imágenes existentes se sirven, ausentes conservan fallback y nombres inválidos devuelven 404 con error estable.
- [x] **T5. Verificar ETag, 304 y cambio de contenido.** RF-5
  - Hecho cuando: sin cambios hay 304 sin cuerpo y al cambiar bytes hay 200 con ETag distinto.
- [x] **T6. Contrastar las 607 URLs con API e inventario.** RF-1, RF-2, RF-4, RF-5
  - Hecho cuando: 607 URLs responden PNG con bytes esperados, cabeceras/304 correctas, cuatro nombres inválidos devuelven 404 y los 300 productos coinciden.
- [x] **T7. Ejecutar pruebas y Ruff, registrando la limitación de Pytest.** RF-4, RF-5, RF-6
  - Hecho cuando: Ruff está aprobado; `uv run python -m pytest` registra 26 passed/1 skipped; `uv run pytest` queda pendiente por `Failed to spawn: pytest`, sin inventar resultado.
- [x] **T8. Validar compatibilidad móvil y documentar evidencia y límites.** RF-3, RF-6
  - Hecho cuando: Android/iOS documentan listas, detalle, carrito, caché fría, reinicio/offline, modo oscuro y texto ampliado; lint/typecheck móvil y cobertura exhaustiva de texto quedan explícitamente pendientes.

## Estado de cierre documental (2026-10-26)

Producción, integración, assets, HTTP, smoke móvil, Ruff y suite alternativa de Pytest están acreditados. La spec está `aprobada`; la implementación y la validación documental aún no se declaran cerradas: `uv run pytest` no pudo iniciar (`Failed to spawn: pytest`) y lint/typecheck móvil no pudieron ejecutarse por dependencias de iCloud, por lo que ambos quedan pendientes.
