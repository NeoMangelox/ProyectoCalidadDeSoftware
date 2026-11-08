#!/usr/bin/env bash
# Se ejecuta una sola vez al crear el volumen del contenedor.
export PGUSER=postgres PGHOST=/var/run/postgresql
bash /benchmark/scripts/setup_databases.sh
