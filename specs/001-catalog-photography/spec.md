# Spec 001 — Fotografía del catálogo

Estado: aprobada

## Contexto y objetivo

Sustituir los degradados visibles del catálogo por fotografía de estudio ficticia, manteniendo la identidad visual de cada producto y la compatibilidad con la aplicación móvil. El alcance comprende los 300 productos del catálogo, con imagen frontal y de detalle para cada uno, además de cinco categorías y dos banners: 607 imágenes en total.

## Usuarios e historias

- HU-1. Como comprador, quiero reconocer el mismo envase en las listas, el detalle y el carrito para identificar el producto con confianza.
- HU-2. Como comprador, quiero que las imágenes del catálogo sigan disponibles tras reiniciar o perder temporalmente la conexión para conservar la continuidad de uso.
- HU-3. Como mantenedor, quiero relacionar cada imagen con su producto, categoría o banner y su referencia de revisión para comprobar la cobertura completa.

## Definiciones

- **Cobertura completa:** dos imágenes de producto por cada uno de los 300 productos, cinco imágenes de categoría y dos banners.
- **Inventario verificable:** relación de cada imagen con su identidad, tipo, dirección de consumo, referencia visual y estado de revisión.

## Requisitos funcionales

- RF-1: ANTES de publicar el lote, EL SISTEMA contrastará la identidad y cobertura de los 300 productos del inventario con el catálogo disponible; cualquier diferencia impedirá declarar completa la entrega.
- RF-2: EL SISTEMA dispondrá de 607 imágenes revisadas: una frontal y una de detalle para cada producto del catálogo, cinco imágenes de categoría y dos banners, todas relacionadas mediante un inventario verificable.
- RF-3: EL SISTEMA representará cada producto con su presentación, nombre en inglés y marca ficticia, sin dosis, claims ni certificaciones añadidas; la imagen de detalle conservará el envase representado en la frontal correspondiente.
- RF-4: CUANDO se solicite una imagen publicada, EL SISTEMA devolverá su contenido conservando la dirección que ya consume la aplicación; los nombres inválidos seguirán sin exponer imágenes.
- RF-5: CUANDO el cliente revalide una imagen cuyo contenido no cambió, EL SISTEMA indicará que no hay contenido nuevo; SI cambió el contenido, devolverá la imagen con un identificador de caché distinto.
- RF-6: EL SISTEMA conservará el catálogo, el inventario, los contratos de datos, las direcciones consumidas y los carritos persistidos, sin crear pedidos como parte de la verificación.

## Requisitos no funcionales

- Las imágenes serán PNG, con fondos claros, luz suave y encuadres cuadrados con margen para productos y categorías; los banners tendrán proporción panorámica sin texto.
- Los nombres de archivo, prompts y metadatos técnicos estarán en inglés; no se añadirán dependencias ni secretos.
- La entrega será reproducible mediante un inventario que incluya referencias y hashes de las imágenes revisadas.
- La comprobación visual móvil cubrirá listas, detalle, carrito, reinicio, caché fría, desconexión temporal, modo oscuro y texto ampliado, registrando explícitamente cualquier cobertura no exhaustiva.

## Casos límite

- Si el catálogo no coincide con el inventario de imágenes, la entrega no se declarará completa.
- Un nombre de imagen inválido no expondrá un archivo.
- Una imagen previamente almacenada puede seguir mostrando un degradado hasta su revalidación o hasta limpiar únicamente la caché de imágenes; no se borrarán los datos del usuario.
- Si la API no está disponible, la verificación viva quedará pendiente y no se sustituirá la fuente persistente por una base compartida.
- Una herramienta de verificación que no pueda ejecutarse por una limitación del entorno se registrará como pendiente, sin convertir una ejecución alternativa en un resultado inexistente.

## Fuera de alcance

- Alojamiento público o publicación fuera del entorno local.
- Rediseño de la aplicación móvil, cambio de contratos, catálogo, inventario, stock, carritos o pedidos.
- Nuevos claims, certificaciones, autenticación, pagos o administración.
- Declarar como aprobadas las comprobaciones móviles, lint o typecheck que no hayan podido ejecutarse.

## Criterios de finalización

- El inventario contiene y relaciona 607 imágenes revisadas: 600 de 300 productos, cinco de categorías y dos banners; no quedan imágenes pendientes.
- El contraste del inventario con el catálogo completo no presenta diferencias y las 59 imágenes de la entrega previa permanecen intactas.
- Las imágenes publicadas responden con su contenido correcto; la revalidación sin cambios y el cambio de contenido cumplen RF-5, y los nombres inválidos conservan el error existente.
- Las pruebas automáticas y la comprobación de formato/lint disponibles quedan registradas con su comando y resultado; las comprobaciones no ejecutables quedan como pendientes explícitos.
- La revisión móvil documenta la evidencia realizada en Android e iOS, incluida la caché fría, el carrito persistido, el modo oscuro y el texto ampliado, sin afirmar cobertura exhaustiva donde no exista.

## Dudas abiertas

- No hay dudas de alcance pendientes. Queda pendiente únicamente repetir lint/typecheck móvil y, si el entorno lo permite, la invocación canónica de Pytest para cerrar la validación técnica; no bloquea la descripción del comportamiento, pero sí el cierre documental de validación.
