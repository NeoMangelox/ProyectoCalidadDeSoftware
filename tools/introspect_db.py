#!/usr/bin/env python3
"""
tools/introspect_db.py
Herramienta de introspeccion para el Agente Autonomo (Fase 1).
Ejecuta introspeccion de information_schema y muestreo de datos con SELECT ... LIMIT 5.
"""

import sys
import psycopg

def introspect(dbname: str):
    print("=" * 60)
    print(f"INTROSPECCION BD: {dbname}")
    print("=" * 60)
    
    conn_info = f"host=localhost port=5432 user=postgres password=postgres dbname={dbname}"
    with psycopg.connect(conn_info) as conn:
        with conn.cursor() as cur:
            # 1. Tablas
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """)
            tables = [r[0] for r in cur.fetchall()]
            print(f"[*] Tablas ({len(tables)}): {', '.join(tables)}")
            
            # 2. Columnas por tabla
            print("\n[*] Detalle de Columnas:")
            for t in tables:
                cur.execute("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name = %s
                    ORDER BY ordinal_position;
                """, (t,))
                cols = cur.fetchall()
                col_str = ", ".join([f"{c[0]} ({c[1]})" for c in cols])
                print(f"  - {t}: {col_str}")

            # 3. Restricciones existentes
            print("\n[*] Claves y Restricciones Existentes:")
            cur.execute("""
                SELECT 
                    tc.table_name, 
                    tc.constraint_name, 
                    tc.constraint_type, 
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu 
                    ON tc.constraint_name = kcu.constraint_name AND tc.table_schema = kcu.table_schema
                LEFT JOIN information_schema.constraint_column_usage ccu 
                    ON ccu.constraint_name = tc.constraint_name AND ccu.table_schema = tc.table_schema
                WHERE tc.table_schema = 'public'
                ORDER BY tc.table_name, tc.constraint_type;
            """)
            constraints = cur.fetchall()
            for c in constraints:
                if c[2] == 'FOREIGN KEY':
                    print(f"  - FK en {c[0]}.{c[3]} -> {c[4]}.{c[5]} ({c[1]})")
                elif c[2] == 'PRIMARY KEY':
                    print(f"  - PK en {c[0]}.{c[3]} ({c[1]})")

            # 4. Muestreo de datos sospechosos (CSV, duplicados, nulos)
            print("\n[*] Muestreo Semantico (LIMIT 5):")
            for t in tables:
                cur.execute(f"SELECT * FROM \"{t}\" LIMIT 5;")
                rows = cur.fetchall()
                cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_schema='public' AND table_name=%s ORDER BY ordinal_position;", (t,))
                colnames = [c[0] for c in cur.fetchall()]
                print(f"\n--- Muestra {t} ({len(rows)} filas) ---")
                for r in rows:
                    row_dict = {colnames[i]: (str(r[i])[:40] if r[i] is not None else 'NULL') for i in range(len(colnames))}
                    print("   ", row_dict)

if __name__ == "__main__":
    db = sys.argv[1] if len(sys.argv) > 1 else "pagila_defective"
    introspect(db)

