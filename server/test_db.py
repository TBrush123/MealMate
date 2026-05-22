import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="postgres",
    user="postgres",
    password="Lolkekchebyrek123!"
)

print("Connection successful!")
conn.close()