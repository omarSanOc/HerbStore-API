# Fotografías del catálogo

Entrega completada: 607 imágenes revisadas: 600 de los 300 productos, cinco categorías y dos banners. El inventario `manifest.json` contiene los datos, prompts, referencias y hashes de las imágenes.

Los archivos finales viven en `app/catalog/assets/{products,categories,banners}/` con los nombres de las URLs existentes. El Dockerfile ya incluye ese directorio al copiar `app/`. No se necesita una subida a un proveedor externo: reconstruir y arrancar la API publica los archivos en las rutas actuales.

## Contraste previo con el catálogo persistente

```bash
uv run python -m scripts.verify_catalog_photography --origin http://localhost:3001 --inventory-only
```

Solo GET: compara Inicio, categorías, catálogo paginado y los 300 detalles. El detalle puede reconciliar estados de pedidos como parte del comportamiento existente del backend. No crea pedidos ni reinicia el stock.

## Comprobación final

```bash
uv run python -m scripts.verify_catalog_photography
uv run python -m scripts.verify_catalog_photography --origin http://localhost:3001
```

La comprobación falla si falta una imagen, el archivo revisado cambió, el formato/proporción es incorrecto o la respuesta HTTP no corresponde a los bytes locales. La segunda forma también verifica inventario, Content-Type, ETag y respuestas 304.

## Caché y app móvil

Se conservan las URLs para mantener carritos persistidos. `Cache-Control: public, max-age=86400` permite conservar la imagen anterior durante 24 horas. Un ETag diferente actúa al revalidar: no invalida inmediatamente una entrada fresca.

La imagen remota de React Native cumple el mismo papel visual que una imagen asíncrona en Compose o SwiftUI: el backend entrega bytes y URL; el componente mantiene espacio, estados de carga/error y caché. No se necesita recompilar el código nativo por este cambio de contenido.

## Entrega original

59/59 PNG generados y revisados, inventario vivo coincidente y archivos publicados en Docker local. Build, Ruff, Pytest (24 passed, 1 skipped), lint, typecheck, smoke móvil (23/23 GET) y 59 URLs con ETag/304 aprobados. Revisión de Inicio, galería y carrito en Samsung USB e iPhone Simulator completada; ver [evidencia y alcance](validation.md). No hay alojamiento público.

## Ampliación completada

548 PNG nuevos para 274 productos, conservando los 59 originales: 607 imágenes revisadas para los 300 productos del catálogo.

La validación móvil Android/iOS se realizó externamente durante la generación y está documentada en `progress.md` y `validation-full-catalog.md`.
