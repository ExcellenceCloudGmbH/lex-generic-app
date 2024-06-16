from django.core.management.base import BaseCommand
import os


class Command(BaseCommand):
    help = 'Renames database objects with a repo name from an environment variable'

    def handle(self, *args, **options):
        # Get the prefix from the environment variable
        prefix_name = os.getenv('LEX_SUBMODEL_REPO_NAME', 'repo_name')  # Set a default in case it's not defined

        sql = f"""
DO $$
DECLARE
    rec record;
    _sql text;
BEGIN
    FOR rec IN
        SELECT c.relname AS old_name,
               n.nspname AS schema_name,
               c.relkind AS type
        FROM pg_class c
        JOIN pg_namespace n ON c.relnamespace = n.oid
        WHERE n.nspname = 'public'
          AND c.relname LIKE 'generic_app_%'
          AND c.relname NOT IN ('generic_app_userchangelog', 'generic_app_log', 'generic_app_calculationlog', 'generic_app_calculationids')
          AND c.relkind IN ('r', 'v', 'S')
    LOOP
        -- Generate the new name based on the type and your naming pattern
        _sql := 'ALTER ' || CASE rec.type
                             WHEN 'r' THEN 'TABLE '
                             WHEN 'v' THEN 'VIEW '
                             WHEN 'S' THEN 'SEQUENCE '
                           END || quote_ident(rec.schema_name) || '.' || quote_ident(rec.old_name) ||
                           ' RENAME TO ' || quote_ident('{prefix_name}' || substr(rec.old_name, 12));

        -- Execute the generated SQL command
        EXECUTE _sql;
    END LOOP;
END $$;
        """

        # Execute the SQL command (Example using Django's connection cursor)
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute(sql)
            self.stdout.write(self.style.SUCCESS('Successfully renamed database objects.'))
