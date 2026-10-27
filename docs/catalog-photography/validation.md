# Validación — 2026-10-19

Resultado: **APROBADO para el alcance local de la spec 001**.

## Trazabilidad

| Requisito | Evidencia | Resultado |
| --- | --- | --- |
| RF-1 | `verify_catalog_photography --origin http://localhost:3001 --inventory-only`, ejecutado antes de generar | Coinciden los 26 productos de Home, 5 categorías y 2 banners; GET de catálogo paginado y 26 detalles |
| RF-2 | `manifest.json` y `verify_catalog_photography` | 59 PNG revisados con prompt, URL, SHA-256 y dimensiones; 52 productos + 7 editoriales |
| RF-3 | Inspección visual individual durante generación; cada detalle usa el frontal como referencia | Marca/nombre inglés coincidentes; presentación adecuada; sin dosis, claims ni certificaciones añadidas; categorías centradas; banners aproximadamente 16:9 |
| RF-4 | 59 respuestas HTTP comparadas byte a byte contra los archivos; `test_catalog_assets.py`; GET de product-300-front y cuatro nombres inválidos | PNG reales, degradado restante idéntico y 404 preservados |
| RF-5 | Verificador HTTP sobre las 59 URLs y prueba de reemplazo de archivo | `image/png`, SHA-1 del contenido en ETag, `public, max-age=86400`, 304 sin cuerpo; cambiar archivo cambia ETag |
| RF-6 | Diff de código; smoke móvil 23/23; revisión móvil y reinicio con carrito | Sin cambios de JSON, catálogo, inventario, persistencia o app; rutas originales reutilizadas |

## Comprobaciones ejecutadas

- `uv run ruff check .` y `uv run ruff format --check .`: aprobados.
- `uv run pytest`: 24 passed, 1 skipped. Se omite la prueba preexistente de concurrencia PostgreSQL en SQLite. Advertencia preexistente de deprecación httpx/Starlette. No se cambió lógica de órdenes ni concurrencia.
- `docker compose build api`: aprobado. Los PNG entran mediante el `COPY app` existente. Contenedor recreado sin recrear la base; seed solo inserta IDs ausentes.
- `uv run python -m scripts.verify_catalog_photography --origin http://localhost:3001`: inventario y 59 archivos/URLs aprobados.
- `npx expo lint`, `npx tsc --noEmit`: aprobados.
- `HERBSTORE_LIVE_API_ORIGIN=http://localhost:3001 npm run verify:live-api`: 23 OK, 0 FAIL; solo GET, sin crear pedidos.
- GET adicional: `/images/products/product-300-front.png` coincide con su degradado; producto 301, categoría inválida, banner inválido y kind inválido devuelven 404.

## Revisión móvil

Muestreo visual en Samsung USB e iPhone 17 Pro Simulator, Development Builds existentes. La revisión de todas las identidades se hizo sobre los 59 originales; la revisión de interacción móvil usa Daily Balance Powder como producto representativo.

- Inicio: fotografía de banners, categorías con recorte circular y tarjetas. Evidencia: [Android](evidence/android-home.png), [iOS](evidence/ios-home.png).
- Galería: frontal y segundo encuadre coherentes. [Android frontal](evidence/android-detail-front.png), [Android detalle](evidence/android-detail-second.png), [iOS frontal](evidence/ios-detail-front.png), [iOS detalle](evidence/ios-detail-second.png).
- Carrito: reutiliza frontal. [Android](evidence/android-cart.png), [iOS](evidence/ios-cart.png).
- Tema oscuro y texto escalado: Android a 2.0 e iOS AX5. La fotografía mantiene proporción y margen dentro de la tarjeta. [Android oscuro/grande](evidence/android-cart-offline-restarted.png), [iOS oscuro/grande](evidence/ios-cart-dark-scaled.png).
- Reinicio: cierre del proceso y apertura de la app, sin limpiar persistencia. [iOS reiniciado](evidence/ios-cart-restarted.png).
- API inaccesible: detener temporalmente solo el contenedor API, mantener Metro; reiniciar ambas apps. Inicio presenta el error de conexión esperado; el carrito conserva el producto y la fotografía previamente cacheada. [Android reiniciado sin API](evidence/android-cart-offline-restarted.png), [iOS reiniciado sin API](evidence/ios-cart-offline-restarted.png). Esto comprueba ausencia del servidor, no modo avión ni descarga de imágenes que nunca estuvieron cacheadas.

Para caché fría se borraron únicamente `cache/image_manager_disk_cache` de Android y `Library/Caches/com.hackemist.SDImageCache` de iOS con la app cerrada. No se limpiaron carrito, preferencias ni pedidos. Antes de hacerlo, Android mostró degradados guardados: confirma la advertencia de 24 horas del README. El cambio de escala Android en caliente mostró temporalmente texto recortado hasta relanzar; se conserva como observación del entorno/UI existente, sin ampliar esta entrega de contenido.

Se restauraron tema claro y escala normal. Queda un producto de prueba en cada carrito para inspección; no se abrió checkout ni se crearon pedidos. Docker API y PostgreSQL quedaron healthy. Metro tuvo que arrancarse con `--lan`: `--localhost` escuchaba solo en IPv6 y el Simulator intentaba IPv4.

## Límites y decisiones

Los PNG suman aproximadamente 107,2 MiB; se conservó calidad del original y no se añadió generación de variantes ni formatos nuevos. La primera descarga será mayor que la de los degradados. Los archivos están en el checkout y la imagen Docker de desarrollo; no se publicaron en Internet. Los otros 274 productos conservan degradados. Las URLs estables mantienen compatibilidad con carritos previos; el ETag nuevo no purga una caché aún fresca.

No se añadieron dependencias, migraciones ni cambios nativos. En Compose o SwiftUI el equivalente sigue siendo una imagen remota con caché: este incremento cambia los bytes servidos por la URL, no el componente móvil.
