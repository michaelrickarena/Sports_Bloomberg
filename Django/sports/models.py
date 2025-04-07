# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta

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
    sport_type = models.TextField()

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
    sport_type = models.TextField()

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
    sport_type = models.TextField()

    class Meta:
        managed = False
        db_table = 'props'

class Spreads(models.Model):
    id = models.BigAutoField(primary_key=True)
    game = models.ForeignKey('Scores', models.DO_NOTHING, to_field='game_id', blank=True, null=True)
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
    sport_type = models.TextField()

    class Meta:
        managed = False
        db_table = 'spreads'


class latest_Moneyline(models.Model):
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
    sport_type = models.TextField()

    class Meta:
        managed = False
        db_table = 'latest_moneyline'



class latest_Overunder(models.Model):
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
    sport_type = models.TextField()

    class Meta:
        managed = False
        db_table = 'latest_overunder'


class latest_Props(models.Model):
    id = models.BigAutoField(primary_key=True)
    game = models.ForeignKey('Scores', models.DO_NOTHING, to_field='game_id', blank=True, null=True)
    last_updated_timestamp = models.DateTimeField()
    bookie = models.TextField()
    prop_type = models.TextField()
    bet_type = models.TextField()
    player_name = models.TextField()
    betting_line = models.BigIntegerField()
    betting_point = models.TextField()
    sport_type = models.TextField()

    class Meta:
        managed = False
        db_table = 'latest_props'

class latest_Spreads(models.Model):
    id = models.BigAutoField(primary_key=True)
    game = models.ForeignKey('Scores', models.DO_NOTHING, to_field='game_id', blank=True, null=True)
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
    sport_type = models.TextField()

    class Meta:
        managed = False
        db_table = 'latest_spreads'


class DistinctProps(models.Model):
    id = models.BigAutoField(primary_key=True)
    player_name = models.CharField(max_length=255)
    game_id = models.CharField(max_length=255)
    sport_type = models.CharField(max_length=255)
    last_updated = models.DateTimeField(auto_now=True)  # Tracks the last update time

    class Meta:
        unique_together = ('player_name', 'game_id', 'sport_type')  # Ensure uniqueness across player_name, game_ID, and sport_type
        db_table = 'distinct_props'
       

    def __str__(self):
        return f"{self.player_name} - {self.game_id} - {self.sport_type}"

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


class UserSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to the user
    stripe_subscription_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    stripe_customer_id = models.CharField(max_length=255, unique=True, null=True, blank=True)  # NEW FIELD
    status = models.CharField(max_length=50, default='trial')
    trial_start_date = models.DateTimeField(default=now)
    expiration_date = models.DateTimeField(null=True, blank=True)
    cancel_date = models.DateTimeField(null=True, blank=True)

    def set_trial_period(self):
        """Automatically set a 7-day trial expiration when the subscription is created."""
        if not self.expiration_date:
            self.expiration_date = now() + timedelta(days=7)

    def save(self, *args, **kwargs):
        """Ensure expiration date is set if in trial status."""
        if self.status == 'trial' and not self.expiration_date:
            self.set_trial_period()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s Subscription"

    class Meta:
        db_table = 'user_subscription'


class UserBet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to user
    game = models.ForeignKey('Scores', on_delete=models.CASCADE, to_field='game_id', blank=True, null=True, db_column='game_id')
    bookie = models.CharField(max_length=50)  # Bookie user bet with
    bet_type = models.CharField(max_length=20, choices=[("moneyline", "Moneyline")])  # Only moneyline for now
    line = models.FloatField()  # Odds user bet at (-110, +120, etc.)
    alert_threshold = models.FloatField()  # % return threshold for alert
    is_active = models.BooleanField(default=True)  # Whether the bet is still being tracked
    team_bet_on = models.CharField(max_length=100, blank=True, null=True)  # Team name user bet on (home or away team)
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when bet was recorded
    bet_amount = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f"{self.user.username} - {self.game_id} ({self.bookie})"

    class Meta:
        db_table = 'userbet'  # Specify the table name explicitly

class ExpectedValueMoneyline(models.Model):
    game_id = models.CharField(max_length=255, db_column='game_id')
    bookie = models.TextField(db_column='bookie')
    matchup_type = models.TextField(db_column='matchup_type')
    team = models.TextField(db_column='team')
    line = models.IntegerField(db_column='line')
    expected_value = models.FloatField(db_column='expected_value')
    fair_probability = models.FloatField(db_column='fair_probability')
    implied_probability = models.FloatField(db_column='implied_probability')
    market_overround = models.FloatField(db_column='market_overround')
    sport_type = models.TextField(db_column='sport_type')
    event_timestamp = models.DateTimeField(db_column='event_timestamp')
    last_updated_timestamp = models.DateTimeField(db_column='last_updated_timestamp')

    class Meta:
        db_table = 'expected_value_moneyline'
        unique_together = ('game_id', 'bookie', 'team', 'line')
        managed = False  # Django won't manage or try to migrate this table

class ExpectedValueProps(models.Model):
    game_ID = models.CharField(max_length=255, db_column='game_id')
    Bookie = models.TextField(db_column='bookie')
    Prop_Type = models.TextField(db_column='prop_type')
    Bet_Type = models.TextField(db_column='bet_type')
    Player_Name = models.TextField(db_column='player_name')
    Betting_Line = models.IntegerField(db_column='betting_line')
    Betting_Point = models.TextField(db_column='betting_point')
    Expected_Value = models.FloatField(db_column='expected_value')
    Fair_Probability = models.FloatField(db_column='fair_probability')
    Implied_Probability = models.FloatField(db_column='implied_probability')
    Market_Overround = models.FloatField(db_column='market_overround')
    sport_type = models.TextField(db_column='sport_type')
    last_updated_timestamp = models.DateTimeField(db_column='last_updated_timestamp')
    Num_Bookies = models.IntegerField(db_column='num_bookies')

    class Meta:
        db_table = 'expected_value_props'
        unique_together = (('game_ID', 'Bookie', 'Prop_Type', 'Bet_Type', 'Player_Name', 'Betting_Line'),)
        managed = False
