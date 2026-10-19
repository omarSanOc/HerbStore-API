# Constitución de HerbStore API

1. **Simplicidad del stack.** Mantendremos el monolito FastAPI, SQLAlchemy, PostgreSQL y Alembic; ninguna dependencia, capa o servicio nuevo entra sin una necesidad verificable y aprobación.
2. **La spec manda.** Todo cambio de comportamiento comienza en una spec aprobada; código, migraciones y tests deben corresponder a sus requisitos y no ampliar su alcance.
3. **Lógica separada de HTTP.** Los routers solo adaptan requests y responses; validación, reglas de negocio y persistencia viven en contratos, servicios y repositorios comprobables de forma aislada.
4. **Tests con las herramientas existentes.** Cada cambio incluye pruebas con Pytest y pasa Ruff; no se instalarán dependencias de testing sin aprobación y la concurrencia se verificará en PostgreSQL.
5. **Datos del usuario protegidos.** Nunca persistiremos ni registraremos direcciones, secretos o valores privados; las claves idempotentes se guardan con hash y los secretos solo mediante variables de entorno.
6. **Idioma consistente.** Código, archivos, identificadores y comentarios técnicos estarán en inglés; documentación en español y textos para usuarios en español e inglés sin alterar campos, enums ni códigos de error.
