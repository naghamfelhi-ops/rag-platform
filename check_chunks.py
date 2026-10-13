import duckdb

print(duckdb.sql('''
    SELECT source, COUNT(*) AS n
    FROM 'data/processed/chunks.parquet'
    GROUP BY source
    ORDER BY n DESC
    LIMIT 5
'''))

print(duckdb.sql("SELECT COUNT(*) AS total_chunks FROM 'data/processed/chunks.parquet'"))
