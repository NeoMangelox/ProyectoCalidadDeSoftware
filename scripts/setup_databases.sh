#!/usr/bin/env bash
# Crea 6 bases (3 casos x {defective, ground_truth}) y carga DDL + datos semilla.
# Uso: PGHOST=127.0.0.1 PGUSER=postgres PGPASSWORD=postgres ./scripts/setup_databases.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
declare -A NAMES=( [case1_pagila]=pagila [case2_northwind]=northwind [case3_synthetic]=synthetic )
for dir in "${!NAMES[@]}"; do
  for kind in defective ground_truth; do
    db="${NAMES[$dir]}_${kind}"
    echo ">> $db"
    psql -q -d postgres -c "DROP DATABASE IF EXISTS $db" -c "CREATE DATABASE $db"
    psql -q -v ON_ERROR_STOP=1 -d "$db" -f "$ROOT/$dir/schema_${kind}.sql" -f "$ROOT/$dir/seed_${kind}.sql"
  done
done
echo "Listo: pagila_*, northwind_*, synthetic_* (defective | ground_truth)"
