# Generated by Django 4.2.19 on 2025-03-16 20:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sports', '0012_userbet_bet_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userbet',
            name='game',
            field=models.ForeignKey(blank=True, db_column='game_id', null=True, on_delete=django.db.models.deletion.CASCADE, to='sports.scores', to_field='game_id'),
        ),
    ]
