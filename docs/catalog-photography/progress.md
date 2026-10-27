# Ampliación del catálogo — avance 2026-10-26

Producción visual, integración Docker y validación móvil Android/iOS completas. La validación móvil se realizó externamente durante la generación de imágenes y está documentada en `validation-full-catalog.md`.

- Vitaminas: 54/54 productos nuevos, 108 PNG.
- Minerales: 55/55 productos nuevos, 110 PNG.
- Proteína: 54/54 productos nuevos, 108 PNG.
- Botánicos: 57/57 productos nuevos, 114 PNG.
- Bienestar: 54/54 productos nuevos, 108 PNG.
- Total: 548 PNG nuevos; 607 imágenes revisadas incluyendo las 59 originales.
- Cobertura: 300 productos con frontal y detalle, cinco categorías y dos banners.
- Verificador local completo aprobado el 26 de octubre: archivos, pares, URLs únicas, proporciones, hashes y preservación exacta de las 59 entradas/imágenes originales.
- Tamaño final: 1,151,496,536 bytes (1098.15 MiB). PNG originales conservados; prompts y referencias en manifest.json.
- Build Docker final y validación HTTP de 607 URLs: aprobados. Ver validation-full-catalog.md para resultados e incidente iCloud resuelto.
- Ruff aprobado; Pytest 26 passed, 1 skipped; smoke 23 OK, 0 FAIL. Lint/typecheck pendientes por lectura de dependencias de iCloud.
- Revisión móvil: iOS revisó Home, galería, carrito, 15 detalles de subcategoría, dark mode y tamaño de texto `extra-extra-large`. El Samsung Android revisó las 15 listas filtradas con imágenes, una galería frontal/detalle, carrito, dark mode y el carrito persistido con miniatura tras reinicio sin API. Se limpió únicamente la caché de imágenes para retirar degradados obsoletos, preservando datos locales; luego se hizo la prueba offline de nuevo y se restauró el carrito vacío. El texto escalado se revisó en ambos dispositivos, no de forma exhaustiva. Ver `validation-full-catalog.md`.
- Lint/typecheck móvil pendientes: node_modules de iCloud no terminó de hidratar y los procesos se quedaron sin CPU; una repetición de Pytest acabó con código 137. Resultados previos aprobados siguen documentados en validation-full-catalog.md.
- Caché HTTP de 24 horas: un degradado previamente almacenado puede seguir visible hasta revalidar; las URLs se mantienen para carritos persistidos.
- Espacio antes del build final: 14 GiB. Base de datos existente arrancada sin recrearla; se conserva su volumen.
