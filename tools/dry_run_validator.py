#!/usr/bin/env python3
"""
tools/dry_run_validator.py
Validador determinista anti-alucinaciones para scripts DDL en PostgreSQL.
Aplica el protocolo transaccional BEGIN ... ROLLBACK para verificar compilacion sin alterar la base de datos.
"""

import os
import sys
import argparse

if sys.platform == "win32":
    for p in [r"C:\Program Files\PostgreSQL\18\bin", r"C:\Program Files\PostgreSQL\16\bin", r"C:\Program Files\PostgreSQL\17\bin"]:
        if os.path.exists(p):
            try:
                os.add_dll_directory(p)
            except Exception:
                pass
            os.environ["PATH"] = p + ";" + os.environ.get("PATH", "")
            break

import psycopg

def validate_ddl(host: str, port: int, user: str, password: str, dbname: str, sql_file: str) -> bool:
    print(f"[*] Iniciando Dry-Run determinista sobre base de datos '{dbname}'...")
    
    try:
        with open(sql_file, "r", encoding="utf-8") as f:
            ddl_content = f.read()
    except FileNotFoundError:
        print(f"[!] Error: No se encontro el archivo SQL '{sql_file}'.")
        return False

    conn_info = f"host={host} port={port} user={user} password={password} dbname={dbname}"

    try:
        # Conexion mediante psycopg v3 (soporta encoding de Windows de forma nativa)
        with psycopg.connect(conn_info, autocommit=False) as conn:
            with conn.cursor() as cursor:
                # Protocolo Dry-Run: transaccion protegida
                cursor.execute("BEGIN;")
                cursor.execute(ddl_content)
                cursor.execute("ROLLBACK;")

        print("[✓] Validacion EXITOSA: El DDL compila al 100% en PostgreSQL sin alucinaciones.")
        return True

    except psycopg.Error as e:
        error_code = getattr(e, "sqlstate", "DESCONOCIDO")
        detalles = str(e).strip()

        print("\n" + "=" * 60)
        print(f"[X] FALLO DE COMPILACION DDL (Codigo PostgreSQL: {error_code})")
        print(f"Detalle: {detalles}")
        print("=" * 60 + "\n")
        return False
    except Exception as ex:
        print(f"[!] Error inesperado: {ex}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validador determinista de DDL PostgreSQL (Dry-Run)")
    parser.add_argument("--host", default="127.0.0.1", help="Host de PostgreSQL (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5432, help="Puerto de PostgreSQL (default: 5432)")
    parser.add_argument("--user", default="postgres", help="Usuario de PostgreSQL (default: postgres)")
    parser.add_argument("--password", default="postgres", help="Contrasena de PostgreSQL (default: postgres)")
    parser.add_argument("--db", default="pagila_defective", help="Base de datos destino (default: pagila_defective)")
    parser.add_argument("--file", required=True, help="Ruta al archivo .sql con el DDL a validar")

    args = parser.parse_args()

    success = validate_ddl(
        host=args.host,
        port=args.port,
        user=args.user,
        password=args.password,
        dbname=args.db,
        sql_file=args.file
    )

    sys.exit(0 if success else 1)