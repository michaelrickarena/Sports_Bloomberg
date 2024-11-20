# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

class AuthGroup(models.Model):
    id = models.BigIntegerField(primary_key=True)  # AutoField?
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigIntegerField(primary_key=True)  # AutoField?
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    id = models.BigIntegerField(primary_key=True)  # AutoField?
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    id = models.BigIntegerField(primary_key=True)  # AutoField?
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigIntegerField(primary_key=True)  # AutoField?
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigIntegerField(primary_key=True)  # AutoField?
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    id = models.BigIntegerField(primary_key=True)  # AutoField?
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    id = models.BigIntegerField(primary_key=True)  # AutoField?
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigIntegerField(primary_key=True)  # AutoField?
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class GeographyColumns(models.Model):
    f_table_catalog = models.TextField(blank=True, null=True)  # This field type is a guess.
    f_table_schema = models.TextField(blank=True, null=True)  # This field type is a guess.
    f_table_name = models.TextField(blank=True, null=True)  # This field type is a guess.
    f_geography_column = models.TextField(blank=True, null=True)  # This field type is a guess.
    coord_dimension = models.BigIntegerField(blank=True, null=True)
    srid = models.BigIntegerField(blank=True, null=True)
    type = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'geography_columns'


class GeometryColumns(models.Model):
    f_table_catalog = models.TextField(blank=True, null=True)  # This field type is a guess.
    f_table_schema = models.TextField(blank=True, null=True)  # This field type is a guess.
    f_table_name = models.TextField(blank=True, null=True)  # This field type is a guess.
    f_geometry_column = models.TextField(blank=True, null=True)  # This field type is a guess.
    coord_dimension = models.BigIntegerField(blank=True, null=True)
    srid = models.BigIntegerField(blank=True, null=True)
    type = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'geometry_columns'

class SpatialRefSys(models.Model):
    srid = models.BigIntegerField(blank=True, null=True)
    auth_name = models.CharField(max_length=256, blank=True, null=True)
    auth_srid = models.BigIntegerField(blank=True, null=True)
    srtext = models.CharField(max_length=2048, blank=True, null=True)
    proj4text = models.CharField(max_length=2048, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'spatial_ref_sys'


class Moneyline(models.Model):
    id = models.BigAutoField(primary_key=True)
    game = models.ForeignKey('Scores', models.DO_NOTHING, to_field='game_id', blank=True, null=True)
    bookie = models.TextField()
    matchup_type = models.TextField()
    home_team = models.TextField()
    line_1 = models.BigIntegerField()
    away_team = models.TextField()
    line_2 = models.BigIntegerField()
    event_timestamp = models.DateTimeField()
    last_updated_timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'moneyline'



class Overunder(models.Model):
    id = models.BigAutoField(primary_key=True)
    game = models.ForeignKey('Scores', models.DO_NOTHING, to_field='game_id', blank=True, null=True)
    bookie = models.TextField()
    matchup_type = models.TextField()
    home_team = models.TextField()
    away_team = models.TextField()
    over_or_under_1 = models.TextField()
    over_under_total_1 = models.FloatField()
    over_under_line_1 = models.BigIntegerField()
    over_or_under_2 = models.TextField()
    over_under_total_2 = models.FloatField()
    over_under_line_2 = models.BigIntegerField()
    event_timestamp = models.DateTimeField()
    last_updated_timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'overunder'


class Props(models.Model):
    id = models.BigAutoField(primary_key=True)
    game = models.ForeignKey('Scores', models.DO_NOTHING, to_field='game_id', blank=True, null=True)
    last_updated_timestamp = models.DateTimeField()
    bookie = models.TextField()
    prop_type = models.TextField()
    bet_type = models.TextField()
    player_name = models.TextField()
    betting_line = models.BigIntegerField()
    betting_point = models.TextField()

    class Meta:
        managed = False
        db_table = 'props'


class Scores(models.Model):
    id = models.BigAutoField(primary_key=True)
    game_id = models.CharField(unique=True, max_length=255, blank=True, null=True)
    sport_title = models.TextField()
    game_time = models.DateTimeField()
    game_status = models.TextField()
    last_updated_timestamp = models.DateTimeField(blank=True, null=True)
    team1 = models.TextField(blank=True, null=True)
    score1 = models.BigIntegerField(blank=True, null=True)
    team2 = models.TextField(blank=True, null=True)
    score2 = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'scores'

class Spreads(models.Model):
    id = models.BigAutoField(primary_key=True)
    game = models.ForeignKey(Scores, models.DO_NOTHING, to_field='game_id', blank=True, null=True)
    bookie = models.TextField()
    matchup_type = models.TextField()
    home_team = models.TextField()
    spread_1 = models.FloatField()
    line_1 = models.BigIntegerField()
    away_team = models.TextField()
    spread_2 = models.FloatField()
    line_2 = models.BigIntegerField()
    event_timestamp = models.DateTimeField()
    last_updated_timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'spreads'


class UpcomingGames(models.Model):
    id = models.BigAutoField(primary_key=True)
    game_id = models.CharField(max_length=255, blank=True, null=True)
    sport_title = models.TextField()
    event_timestamp = models.DateTimeField()
    home_team = models.TextField()
    away_team = models.TextField()

    class Meta:
        managed = False
        db_table = 'upcoming_games'
