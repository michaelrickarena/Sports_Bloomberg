from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('sports', '0013_alter_userbet_game'),  # Replace with the last applied migration
    ]

    operations = [
        # Drop the existing constraint
        migrations.RunSQL(
            sql="""
            ALTER TABLE userbet
            DROP CONSTRAINT userbet_game_id_c8586449_fk_scores_game_id;
            """,
            reverse_sql="""
            ALTER TABLE userbet
            ADD CONSTRAINT userbet_game_id_c8586449_fk_scores_game_id
            FOREIGN KEY (game_id) REFERENCES scores (game_id) ON DELETE NO ACTION;
            """
        ),
        # Add the new constraint with ON DELETE CASCADE
        migrations.RunSQL(
            sql="""
            ALTER TABLE userbet
            ADD CONSTRAINT userbet_game_id_c8586449_fk_scores_game_id
            FOREIGN KEY (game_id) REFERENCES scores (game_id) ON DELETE CASCADE;
            """,
            reverse_sql="""
            ALTER TABLE userbet
            DROP CONSTRAINT userbet_game_id_c8586449_fk_scores_game_id;
            """
        ),
    ]