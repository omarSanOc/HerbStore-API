# Validación de la ampliación — 2026-10-26

## Resultado actual

Producción e integración completas: 548 PNG nuevos para 274 productos. El catálogo tiene 607 imágenes revisadas: 300 pares de producto, cinco categorías y dos banners. Tamaño: 1,151,496,536 bytes (1,098.15 MiB). Prompts, referencias frontales, dimensiones y SHA-256 están en manifest.json. Las 59 entradas e imágenes originales permanecen intactas.

## Comprobaciones aprobadas

- Verificador local completo: 607/607, sin pendientes, URLs/archivos únicos, pares, proporciones, hashes y baseline original.
- Inventario HTTP: /home, /categories, catálogo paginado y 300 detalles coinciden con nombres, marcas, descripciones, categorías y URLs.
- Cuatro URLs inválidas verificadas vía HTTP: 404.
- 607 URLs: HTTP 200, bytes idénticos a PNG aprobados, image/png, ETag SHA-1, Cache-Control public, max-age=86400 y 304 sin cuerpo.
- Ruff: aprobado en el repositorio.
- Pytest: 26 passed, 1 skipped; incluye archivo ausente/fallback, 404, ETag al reemplazar archivo y manifiesto completo. Ejecutado con dependencias del mismo uv.lock en copia temporal fuera de iCloud. La omisión corresponde al test PostgreSQL preexistente sobre SQLite; advertencia preexistente de httpx/Starlette.
- Build Docker final aprobado. Config de imagen: sha256:222e5ca023bdf8cd4b7be5f9abef286dc2fc324c5aa77a0617eda6e225aa34e6. API recreada con compose up -d --no-deps --no-build api. Se arrancó la base de datos existente, que estaba detenida; no se recreó su contenedor/volumen.
- Smoke de la app: 23 OK, 0 FAIL, exclusivamente GET, sin pedidos.

## Incidente resuelto del build

iCloud retiró archivos locales durante la copia de Docker; el primer build incluyó al menos un PNG vacío (product-281-front). La verificación HTTP lo detectó y esa imagen Docker fue reemplazada. Se preparó un contexto temporal fuera de iCloud con el mismo código, restaurando imágenes desde los originales generados por SHA-256; los 607 archivos pasaron el verificador antes del build y todas las URLs después. Se eliminaron únicamente las copias temporales de los PNG al finalizar para recuperar espacio. Los originales generados y los archivos del repositorio se conservan.

## Validación móvil

- iOS 26.5, iPhone 17 Pro Simulator: Home, frontal y detalle (swipe) de product-006, y carrito con su imagen frontal se revisaron visualmente. Citrus C Powder se añadió para verificar el carrito y después se retiró, preservando el artículo que ya existía. También se recorrió una pantalla de detalle/galería por cada una de las 15 subcategorías; el árbol accesible confirmó el nombre esperado. Las capturas están en `evidence/ios-subcategories/` y `evidence/herbstore-ios-*`.
- Android, Samsung SM-A037M: se capturaron y revisaron visualmente las listas filtradas de las 15 subcategorías. Cada lista muestra 20 productos; la evidencia está en `evidence/android-subcategories/`. En una tarjeta nueva de Minerales se abrió Calcium Balance Tabletas, se comprobó la imagen frontal y el swipe a la imagen de detalle; se agregó al carrito para verificar su miniatura y se retiró después. El carrito quedó vacío, como al inicio de esta comprobación; no se crearon pedidos.
- La primera revisión reveló degradados antiguos en algunas tarjetas por la caché persistente del teléfono, aunque la API devolvía los PNG correctos. Se eliminó únicamente `cache/image_manager_disk_cache` del paquete Android y se reinició la app sin borrar sus datos. Tras la caché fría cargaron las imágenes reales en las tarjetas de Botánicos, Home y las subcategorías; las capturas Android de las 15 listas se guardaron después de ello.
- Offline Android: se agregó temporalmente Calcium Balance Tabletas, se detuvo la API, se forzó el cierre y se volvió a abrir la app. Tras abrir el carrito, permanecieron el producto persistido y su miniatura cacheada. La captura es `evidence/android-cart-offline-restarted-new.png`. Se reanudó la API y, en línea, se eliminó el artículo temporal; el carrito quedó vacío. No se crearon pedidos.
- Tema oscuro: comprobado visualmente en Android (`evidence/android-cart-dark-mode.png`) y en iOS (`evidence/ios-subcategory-dark-mode.png`); ambos se restauraron a claro. El tamaño de texto se elevó temporalmente a 1.3 en Android y `extra-extra-large` en iOS, y se restauró a 1.0/`large`. La captura iOS está en `evidence/ios-subcategory-scaled-text.png`; controles y subcategorías siguen accesibles con desplazamiento, aunque no se recorrió toda la app a ese tamaño. El intento anterior de Dynamic Type AX5 devolvió `Invalid argument`; un tamaño estándar soportado sí funcionó.
- Lint y typecheck móviles siguen pendientes: el `node` del PATH no está configurado; al usar el Node incluido por Codex, ambos procesos quedaron bloqueados sin CPU al acceder a `node_modules` de iCloud. Una repetición de Ruff/Pytest se intentó durante esta continuación; el proceso terminó con código 137 sin producir resultados, en un momento en que el disco tenía 2.2 GiB libres. Se mantienen los resultados previos aprobados de Ruff y Pytest descritos arriba.
- El modo offline con carrito persistido e imagen cacheada quedó probado después de limpiar la caché de imágenes en Android y también en iOS. El texto escalado se revisó brevemente en Android con escala 1.3 y se restauró a 1.0; no se recorrió toda la cobertura del plan a esa escala. API local permanece healthy.

## Caché y límites

Las URLs no cambian. La app usa caché de imágenes de 24 horas, así que una imagen fallback/degradada almacenada previamente puede seguir mostrándose hasta revalidar o hasta limpiar solo la caché de imágenes de la app; el ETag nuevo se aplica al revalidar. Alojamiento exclusivamente Docker local, sin publicación pública. No se cambiaron contratos, catálogo, stock ni persistencia; no se crearon pedidos. validation.md conserva la evidencia histórica de la entrega de 59 imágenes y no acredita esta ampliación móvil.
