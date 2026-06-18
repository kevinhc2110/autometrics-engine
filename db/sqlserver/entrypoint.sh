#!/bin/bash
set -e

/opt/mssql/bin/sqlservr &

# Wait for SQL Server to start
echo "⏳ Waiting for SQL Server to start..."
for i in {1..60}; do
    if /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "$MSSQL_SA_PASSWORD" -C -Q "SELECT 1" &>/dev/null; then
        echo "✅ SQL Server is ready."
        break
    fi
    sleep 2
done

# Run init script
echo "📦 Running init.sql..."
/opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "$MSSQL_SA_PASSWORD" -C -d master -i /init.sql
echo "✅ Init complete."

# Keep container running
wait
