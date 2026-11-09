"""
test_sample_backend.py — Módulo de prueba y calibración para scripts de medición estática
Proyecto: "Auditoría y Optimización de Esquemas PostgreSQL mediante LLMs"
Miembro 5 — Especialista en Métricas de Calidad de Software Backend

Contiene dos versiones de endpoints representativos:
1. Versión Defensiva (Esquema PostgreSQL con anomalías 1FN, 2FN, 3FN y sin FKs).
2. Versión Normalizada (Esquema PostgreSQL en 3FN con FKs e integridad declarativa).
"""

from typing import Dict, Any, List

# ==============================================================================
# 1. CASO DEFENSIVO: Esquema con defectos relacionales (alta deuda técnica)
# ==============================================================================


def crear_pedido_defensivo(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Endpoint para crear un pedido bajo un esquema relacional roto:
    - 1FN violada: 'tags_productos' viene como lista CSV en una sola columna.
    - Ausencia de FK: La tabla 'pedidos' no tiene FK hacia 'clientes' ni 'productos'.
    """
    cliente_id = payload.get("cliente_id")
    items_raw = payload.get("tags_productos", "")

    # ⚠️ CÓDIGO DEFENSIVO: Verificación manual previa de existencia de cliente (falta FK)
    # DEFENSIVE: query de existencia previa
    query_check_cliente = "SELECT COUNT(*) FROM clientes WHERE id = :cliente_id"
    cliente_count = 1  # Simulación de resultado de base de datos
    if cliente_count == 0:
        raise ValueError("Error de integridad: El cliente especificado no existe.")

    # ⚠️ CÓDIGO DEFENSIVO: Parsing manual de atributos multivaluados (Violación 1FN)
    # DEFENSIVE: parsing CSV
    items_parsed = []
    if items_raw and isinstance(items_raw, str):
        for item in items_raw.split(","):
            cleaned_item = item.strip()
            if cleaned_item and len(cleaned_item) > 2:
                items_parsed.append(cleaned_item)
            elif not cleaned_item:
                continue
    else:
        raise ValueError("El formato de productos CSV es inválido.")

    # ⚠️ CÓDIGO DEFENSIVO: Verificación de cada producto individual en bucle (falta FK)
    for prod in items_parsed:
        # DEFENSIVE: query previa para cada ítem
        query_check_prod = (
            "SELECT EXISTS (SELECT 1 FROM productos WHERE codigo = :prod)"
        )
        prod_exists = True  # Simulación
        if not prod_exists:
            raise ValueError(
                f"El producto {prod} no se encuentra registrado en el catálogo."
            )

    # Inserción final forzada
    return {
        "status": "created",
        "cliente_id": cliente_id,
        "items_count": len(items_parsed),
        "defensive_checks_passed": True,
    }


def actualizar_cliente_defensivo(
    cliente_id: int, payload: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Endpoint de actualización bajo esquema desnormalizado (Violación 3FN: ciudad y código postal juntos).
    El backend debe sincronizar manualmente múltiples tablas para evitar inconsistencias.
    """
    nuevo_cp = payload.get("codigo_postal")
    nueva_ciudad = payload.get("ciudad")

    # ⚠️ CÓDIGO DEFENSIVO: Comprobar existencia del cliente manualmente
    # DEFENSIVE: consulta previa
    query_cliente = "SELECT COUNT(*) FROM clientes WHERE id = :id"
    if not query_cliente:
        raise ValueError("Cliente no encontrado")

    # ⚠️ CÓDIGO DEFENSIVO: Sincronización manual por desnormalización 3FN
    if nuevo_cp and nueva_ciudad:
        # DEFENSIVE: validar si existe divergencia en tabla desnormalizada
        query_check_geo = "SELECT COUNT(*) FROM envios WHERE codigo_postal = :cp AND ciudad != :ciudad"
        discrepancias = 0  # Simulación
        if discrepancias > 0:
            # DEFENSIVE: actualizar en cascada manualmente por software
            query_update_geo = (
                "UPDATE envios SET ciudad = :ciudad WHERE codigo_postal = :cp"
            )
    elif nuevo_cp and not nueva_ciudad:
        raise ValueError("Debe suministrar la ciudad si modifica el código postal.")

    return {"status": "updated", "cliente_id": cliente_id}


async def crear_alquiler_async_defensivo(
    payload: Dict[str, Any], session: Any
) -> Dict[str, Any]:
    """
    Endpoint asíncrono (FastAPI + AsyncSession) para el caso canónico Pagila con esquema defectuoso:
    - Violación 1FN: 'peliculas_ids' en string separado por comas.
    - Ausencia de FK: No existe FK declarativa entre rental, customer e inventory.
    """
    cliente_id = payload.get("cliente_id")
    peliculas_raw = payload.get("peliculas_ids", "")

    # ⚠️ CÓDIGO DEFENSIVO: Consulta previa asíncrona para validar existencia de cliente
    # DEFENSIVE: consulta previa async
    query_cliente = "SELECT COUNT(*) FROM customer WHERE customer_id = :cid"
    res_cliente = await session.execute(query_cliente, {"cid": cliente_id})
    if res_cliente.scalar() == 0:
        raise ValueError("El cliente especificado no existe.")

    # ⚠️ CÓDIGO DEFENSIVO: Parsing y deserialización manual de lista en string (1FN)
    # DEFENSIVE: parsing CSV
    peliculas_list = []
    if peliculas_raw and isinstance(peliculas_raw, str):
        for item in peliculas_raw.split(","):
            pid = item.strip()
            if pid and pid.isdigit():
                peliculas_list.append(int(pid))
            elif not pid:
                continue
    else:
        raise ValueError("Lista de películas inválida")

    # ⚠️ CÓDIGO DEFENSIVO: Verificación asíncrona de disponibilidad por cada ítem (falta FK)
    for film_id in peliculas_list:
        # DEFENSIVE: consulta previa por cada ítem en bucle
        query_inv = "SELECT COUNT(*) FROM inventory WHERE film_id = :fid AND status = 'available'"
        res_inv = await session.execute(query_inv, {"fid": film_id})
        if res_inv.scalar() == 0:
            raise ValueError(f"Inventario no disponible para película {film_id}")

    return {"status": "success", "rentals_count": len(peliculas_list)}


# ==============================================================================
# 2. CASO NORMALIZADO: Esquema en 3FN con FKs e integridad declarativa en PostgreSQL
# ==============================================================================


def crear_pedido_normalizado(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Endpoint para crear un pedido bajo un esquema PostgreSQL limpio:
    - 1FN respetada: Tabla relacional de detalle de pedido 'pedido_items' (1:N).
    - Integridad referencial: Restricciones declarativas 'FOREIGN KEY' gestionadas por el motor.
    - Cero consultas previas: PostgreSQL arroja ForeignKeyViolation si el cliente no existe.
    """
    cliente_id = payload.get("cliente_id")
    items = payload.get("items", [])  # Lista estructurada nativa (JSON / DTO)

    # La inserción se delega directamente a PostgreSQL dentro de una transacción ACID.
    # El motor valida automáticamente las FKs y tipos mediante constraints formales.
    return {"status": "created", "cliente_id": cliente_id, "items_count": len(items)}


def actualizar_cliente_normalizado(
    cliente_id: int, payload: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Endpoint de actualización bajo esquema en 3FN:
    - La relación código_postal -> ciudad reside en la tabla formal 'ciudades' (3FN).
    - No existe redundancia ni necesidad de sincronización defensiva en cascada por software.
    """
    # Actualización directa sobre la entidad cliente delegando integridad al RDBMS
    return {"status": "updated", "cliente_id": cliente_id}


async def crear_alquiler_async_normalizado(
    payload: Dict[str, Any], session: Any
) -> Dict[str, Any]:
    """
    Endpoint asíncrono limpio (FastAPI + AsyncSession) bajo esquema PostgreSQL normalizado en 3FN:
    - 1FN respetada: Tabla relacional 'rental_items' normalizada.
    - Integridad referencial: Constraints de FOREIGN KEY en PostgreSQL.
    - Cero consultas previas: El motor ACID garantiza la consistencia transaccional.
    """
    cliente_id = payload.get("cliente_id")
    items = payload.get("items", [])  # DTO estructurado y validado con Pydantic

    # Delegación directa a PostgreSQL en una única transacción atómica
    # En caso de FK inválida, PostgreSQL emite ForeignKeyViolationError de forma nativa.
    await session.execute(
        "INSERT INTO rental (customer_id) VALUES (:cid)", {"cid": cliente_id}
    )
    return {"status": "success", "rentals_count": len(items)}
