# Plan 001 — Fotografía del catálogo

Este plan queda alineado con la spec implementada y describe únicamente la entrega ya realizada de 607 imágenes para el catálogo completo. No autoriza ampliar el comportamiento ni cambiar contratos.

## RF-1 — Contraste del catálogo completo

- **Archivos y responsabilidades:** `docs/catalog-photography/manifest.json` mantiene la relación de 300 productos y 607 imágenes; `scripts/verify_catalog_photography.py` valida conteos, pares, unicidad, hashes y correspondencia con el inventario vivo; `tests/test_catalog_assets.py` cubre el manifiesto completo y la detección de diferencias.
- **Flujo HTTP y de datos:** el verificador consulta Home, categorías, catálogo paginado y detalle; compara identidad, metadatos e imágenes declaradas con el manifiesto y recorre los 300 productos.
- **Lógica aislable:** validar el manifiesto, seleccionar elementos revisados y verificar originales son operaciones separables de la consulta HTTP.
- **Contratos JSON/OpenAPI:** se conservan los campos y direcciones JSON existentes; no se añade ni renombra ningún campo.
- **Persistencia/migraciones:** no aplica; no se cambia el modelo persistente ni se requiere migración.
- **Transacciones/concurrencia:** el tráfico del verificador es exclusivamente GET y no crea pedidos. No se describe como estrictamente libre de mutaciones internas: el detalle de producto puede reconciliar estados y confirmar la transacción. Según confirmación externa explícita del usuario, las comparaciones realizadas antes y después de la validación mostraron inventario/stock y órdenes existentes sin cambios.
- **i18n/privacidad:** se consulta el inventario en inglés para comparar valores estables; no se registran datos privados.
- **Errores:** cualquier diferencia, archivo ausente o hash incorrecto detiene la declaración de cobertura completa.
- **Pytest/Ruff/PostgreSQL:** `uv run python -m pytest` pasó 26 tests con 1 omitido; se conserva la evidencia de que `uv run pytest` no pudo iniciar por `Failed to spawn: pytest`, sin requerir su repetición. Ruff quedó aprobado. No se requiere PostgreSQL.

## RF-2 — Cobertura y revisión de 607 imágenes

- **Archivos y responsabilidades:** `app/catalog/assets/` contiene los PNG publicados; `manifest.json` registra 600 imágenes de producto, cinco de categoría y dos banners; `verify_catalog_photography.py` comprueba tipo, dimensiones, pares, estado revisado y SHA-256.
- **Flujo HTTP y de datos:** cada elemento se comprueba localmente y, cuando hay origen disponible, se solicita su dirección publicada y se compara el cuerpo con el archivo aprobado.
- **Lógica aislable:** la validación de PNG, proporciones, hashes y cobertura por categoría se ejecuta sin depender del renderizado móvil.
- **Contratos JSON/OpenAPI:** listas, detalle, Home y categorías conservan sus campos e imágenes declaradas; no hay cambios de contrato.
- **Persistencia/migraciones:** no aplica. **Transacciones/concurrencia:** no aplica.
- **i18n/privacidad:** nombres y prompts siguen en inglés; no se incorpora información de usuario.
- **Errores:** un PNG vacío, inválido, duplicado, pendiente o con proporción/hash incorrectos hace fallar la verificación.
- **Pytest/Ruff/PostgreSQL:** el test de manifiesto confirma 300 productos y 607 assets; la suite alternativa pasó 26/1. Ruff aprobado. PostgreSQL no es necesario.

## RF-3 — Fidelidad visual y coherencia frontal/detalle

- **Archivos y responsabilidades:** el manifiesto conserva marca, nombre, presentación, referencia frontal, prompt y estado de revisión; la evidencia visual se mantiene en `docs/catalog-photography/`.
- **Flujo HTTP y de datos:** las imágenes se sirven según la relación producto/visual del manifiesto; la revisión confirma que frontal y detalle representan el mismo envase.
- **Lógica aislable:** el verificador valida la relación de pares y la evidencia documental acredita la revisión visual.
- **Contratos JSON/OpenAPI:** no se modifican nombre, marca, descripción, enums ni forma de las respuestas.
- **Persistencia/migraciones:** no aplica. **Transacciones/concurrencia:** no aplica.
- **i18n/privacidad:** no se añaden claims ni datos personales.
- **Errores:** cualquier divergencia visual se registra y evita marcar ese elemento como revisado.
- **Pytest/Ruff/PostgreSQL:** la comprobación de pares y la evidencia cubren RF-3; no hay requisito específico de PostgreSQL.

## RF-4 — Publicación, direcciones y nombres inválidos

- **Archivos y responsabilidades:** `app/catalog/routes.py` conserva la resolución, validación y fallback; `app/catalog/image_files.py` conserva la lectura de archivos.
- **Flujo HTTP y de datos:** una solicitud validada busca el PNG correspondiente; un archivo inexistente conserva el fallback y un nombre inválido conserva 404.
- **Lógica aislable:** selección, existencia y decisión fallback/404 están cubiertas por tests de catálogo.
- **Contratos JSON/OpenAPI:** se mantienen direcciones, status y respuestas; errores conservan envelope/código.
- **Persistencia/migraciones:** no aplica. **Transacciones/concurrencia:** no aplica.
- **i18n/privacidad:** se mantienen códigos/idiomas; no se exponen rutas privadas.
- **Errores:** se verifica archivo ausente, nombre desconocido y nombre fuera de colecciones públicas.
- **Pytest/Ruff/PostgreSQL:** tests de fallback y 404; suite alternativa 26 passed/1 skipped; Ruff aprobado. PostgreSQL no aplica.

## RF-5 — Revalidación y caché

- **Archivos y responsabilidades:** `app/catalog/routes.py` conserva ETag derivado del contenido y cabeceras; `tests/test_catalog_assets.py` verifica 200, 304 y cambio de ETag.
- **Flujo HTTP y de datos:** la primera solicitud devuelve bytes y ETag; el mismo ETag devuelve 304 sin cuerpo; contenido cambiado devuelve 200 y ETag distinto.
- **Lógica aislable:** cálculo/comparación de ETag y lectura de bytes se prueban sin base de datos.
- **Contratos JSON/OpenAPI:** se preservan `image/png`, `Cache-Control` de 24 horas y la semántica 304.
- **Persistencia/migraciones:** no aplica. **Transacciones/concurrencia:** no aplica.
- **i18n/privacidad:** no contiene textos ni datos privados.
- **Errores:** un cambio de archivo no sirve contenido vacío ni reutiliza el ETag anterior.
- **Pytest/Ruff/PostgreSQL:** test de revalidación; suite alternativa 26/1 y Ruff aprobado. PostgreSQL no aplica.

## RF-6 — Compatibilidad y validación de la aplicación

- **Archivos y responsabilidades:** `docs/catalog-photography/progress.md` y `validation-full-catalog.md` concentran estado y evidencia; no se tocan catálogo, stock, pedidos o carritos.
- **Flujo HTTP y de datos:** la aplicación consume las mismas direcciones; se verifican listas, detalle, carrito, reinicio y offline sin crear pedidos. El smoke registrado usó exclusivamente GET; esos GET pueden reconciliar estado internamente, por lo que la ausencia de cambios no se infiere del método HTTP.
- **Lógica aislable:** la comprobación de compatibilidad es validación de contrato y evidencia móvil, separada de la generación.
- **Contratos JSON/OpenAPI:** smoke exclusivamente GET, 23 OK/0 FAIL; no se alteran envelopes, campos, status ni idiomas.
- **Persistencia/migraciones:** no hay cambios ni migraciones; se preserva el carrito existente. **Transacciones/concurrencia:** según confirmación externa explícita del usuario, las comparaciones realizadas antes y después de la validación mostraron inventario/stock y órdenes existentes sin cambios; esta conclusión no se atribuye únicamente al tráfico GET.
- **i18n/privacidad:** no se registran datos privados; modo oscuro y texto ampliado no cambian datos.
- **Errores:** una caché antigua puede mostrar un degradado hasta la revalidación; la validación móvil externa y sus límites quedan documentados.
- **Pytest/Ruff/PostgreSQL:** Ruff aprobado; `uv run python -m pytest` 26/1; se conserva que `uv run pytest` falló al crear el proceso (`Failed to spawn: pytest`) y que la repetición posterior terminó con código 137, sin atribuirles un resultado satisfactorio ni requerir nuevas ejecuciones. El lint y el typecheck móviles finalizaron satisfactoriamente según confirmación externa del usuario. PostgreSQL no requiere cambios.

## Decisiones y alternativas descartadas

- Se conserva el almacenamiento local de PNG y las direcciones existentes para evitar proveedor externo y cambios móviles; publicar en un servicio nuevo queda fuera de alcance.
- Se calcula el ETag desde el contenido para hacer observable un cambio real; se descarta invalidación global inmediata porque la caché de 24 horas es existente.
- Se conserva la ejecución alternativa de Pytest como evidencia válida sin convertirla en resultado de la invocación canónica fallida ni repetir pruebas ya aprobadas; se descarta inventar un resultado.
