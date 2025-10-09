import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute('SELECT * FROM imtemptrn LIMIT 0')
    columns = [desc[0] for desc in cursor.description]
    print('Table columns:', columns)
    
    # Check if there's an id column
    if 'id' in columns:
        print('Table HAS an id column')
    else:
        print('Table does NOT have an id column')
        
    # Check primary key using simpler query
    cursor.execute("""
        SELECT column_name
        FROM information_schema.key_column_usage 
        WHERE table_name = 'imtemptrn' 
        AND constraint_name LIKE '%pkey%'
    """)
    
    pk_columns = [row[0] for row in cursor.fetchall()]
    print('Primary key columns:', pk_columns)