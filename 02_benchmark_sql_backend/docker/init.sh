#!/usr/bin/env bash
# Se ejecuta una sola vez al crear el volumen del contenedor.
export PGUSER=postgres PGHOST=/var/run/postgresql
bash /benchmark/02_benchmark_sql_backend/scripts/setup_databases.sh
