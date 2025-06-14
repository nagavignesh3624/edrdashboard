import os
from django.core.management.base import BaseCommand
import psycopg2

class Command(BaseCommand):
    help = 'List tables and validate user in the database using psycopg2.'

    def get_db_connection(self):
        db_url = os.getenv(
            'DATABASE_URL',
            'postgresql://15249:"UsIcVNmqZo5@192.168.12.35:5432/RFDB_Server'
        )
        return psycopg2.connect(db_url)

    def add_arguments(self, parser):
        parser.add_argument('--columns', type=str, help='Show columns for the given table name')

    def handle(self, *args, **options):
        table_name = options.get('columns')
        if table_name:
            self.show_columns(table_name)
            return
        self.stdout.write(self.style.SUCCESS('Listing all tables in public schema:'))
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
                    tables = [row[0] for row in cur.fetchall()]
                    for table in tables:
                        self.stdout.write(f'- {table}')
        except Exception as e:
            self.stderr.write(f'Error listing tables: {e}')

    def show_columns(self, table_name):
        self.stdout.write(self.style.SUCCESS(f'Columns for table: {table_name}'))
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = %s;", (table_name,))
                    columns = cur.fetchall()
                    for col, dtype in columns:
                        self.stdout.write(f'- {col} ({dtype})')
        except Exception as e:
            self.stderr.write(f'Error fetching columns: {e}')

        # Optional: Validate a user (uncomment to use)
        # username = input('Enter username: ')
        # password = input('Enter password: ')
        # if self.validate_user(username, password):
        #     self.stdout.write(self.style.SUCCESS('Login successful'))
        # else:
        #     self.stderr.write('Invalid credentials')

    def validate_user(self, username, password):
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT 1 FROM employee WHERE username=%s AND password=%s LIMIT 1;",
                        (username, password)
                    )
                    return cur.fetchone() is not None
        except Exception as e:
            self.stderr.write(f'Login validation error: {e}')
            return False
