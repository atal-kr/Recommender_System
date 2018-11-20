from django.db import models
from django_mysql.models import ListCharField
# Create your models here.


class User(models.Model):
    "represent User details in db."
    user_id = models.BigIntegerField(primary_key=True)
    country = models.CharField(max_length=50,null=True)
    state = models.CharField(max_length=50,null=True)
    city = models.CharField(max_length=50,null=True)
    gender = models.CharField(max_length=10,null=True)
    age = models.CharField(max_length=15,null=True)
    language = models.CharField(max_length=200,null=True,default=None,db_column='user_language')
    user_preferences=models.CharField(max_length=200,default=None,null=True,db_column='content_language')

    class Meta:
        db_table = 'user_data'

class User_AB(models.Model):
    "represent User details in db."
    user_id = models.BigIntegerField(primary_key=True)
    group = models.CharField(max_length=20,null=True)
    class Meta:
        db_table = 'users_ab'

    @classmethod
    def user_list(cls,group=None):
        if not group:
            return cls.objects.all().values_list('user_id',flat=True)
        return cls.objects.filter(group=group).values_list('user_id',flat=True)


class LastContentPlayed(models.Model):
        '''it has record of user last played content and user circle.'''
        user_id = models.BigIntegerField(primary_key=True)
        uu_played = models.IntegerField(null=True, db_column='UU_PLAYED')
        session = models.IntegerField(null=True, db_column='SESSIONS')
        circle = models.CharField(max_length=50, db_column='CIRCLE', db_index=True)
        mou = models.DecimalField(null=True, max_digits=15, decimal_places=5, db_column='mou')
        last_date  = models.DateField(db_column='last_played_date')
        content_id = models.CharField(max_length=50,db_column='last_played_content_id')
        content_type = models.CharField(max_length=20,db_column='last_played_content_type')
        class Meta:
            db_table= 'user_played_data'


class Decider(models.Model):
    """its decider model ."""
    recomm_bucket = models.CharField(null=True,max_length=150,db_column='recommendation_bucket',db_index=True)
    recomm_id = models.IntegerField(null=True,db_column='recommendation_id')
    gender = models.CharField(db_index=True,null=True,max_length=10,db_column='gender')
    state=models.CharField(null=True,max_length=50)
    language = models.CharField(db_index=True,null=True,max_length=50,db_column='language')
    id = models.AutoField(primary_key=True, null=False)

    class Meta:
        db_table = 'decider'
        unique_together = ('recomm_bucket','gender','language')


class Recommendation(models.Model):
    """represent recommendation model."""
    recomm_id = models.IntegerField(db_index=True,null=True,db_column='recommendation_id')
    content_seen=models.CharField(max_length=50,db_index=True,null=True,db_column='content_seen')
    content_recommended=models.CharField(max_length=50,null=True,db_column='content_recommended')
    support_12 = models.FloatField(null=True)
    support_1 = models.FloatField(null=True)
    support_2 = models.FloatField(null=True)
    confidence = models.FloatField(null=True)
    lift = models.FloatField(null=True)
    id = models.AutoField(primary_key=True, null=False)

    class Meta:
        db_table = 'recommendation_base'

    def __str__(self):
        return str(self.content_recommended)+":"+ str(self.confidence)
    def __hash__(self):
        return self.content_recommended.__hash__()

    def __eq__(self, other):
        return self.content_recommended == other.content_recommended

class TVRecommendation(models.Model):
    """represent recommendation model."""
    recomm_id = models.IntegerField(db_index=True,null=True,db_column='recommendation_id')
    content_seen=models.CharField(max_length=50,db_index=True,null=True,db_column='content_seen')
    content_recommended=models.CharField(max_length=50,null=True,db_column='content_recommended')
    support_12 = models.FloatField(null=True)
    support_1 = models.FloatField(null=True)
    support_2 = models.FloatField(null=True)
    confidence = models.FloatField(null=True)
    lift = models.FloatField(null=True)
    id = models.AutoField(primary_key=True, null=False)

    class Meta:
        db_table = 'recommendation_base_tv'

    def __str__(self):
        return str(self.content_recommended)+":"+ str(self.confidence)
    def __hash__(self):
        return self.content_recommended.__hash__()

    def __eq__(self, other):
        return self.content_recommended == other.content_recommended
class Recommendation_Content(models.Model):
        """represent recommendation model. for content_based recommendation"""
        recomm_id = models.IntegerField(db_index=True, null=True, db_column='recommendation_id')
        content_seen = models.CharField(max_length=50, db_index=True, null=True, db_column='content_seen')
        content_recommended = models.CharField(max_length=50, null=True, db_column='content_recommended')
        confidence = models.FloatField(null=True)
        actor_score = models.FloatField(null=True)
        genre_score = models.FloatField(null=True)
        streams = models.FloatField(null=True)
        id = models.AutoField(primary_key=True, null=False)

        class Meta:
            db_table = 'recommendation_content'

        def __str__(self):
            return str(self.content_recommended) + ":" + str(self.confidence)

        def __hash__(self):
            return self.content_recommended.__hash__()

        def __eq__(self, other):
            return self.content_recommended == other.content_recommended

def get_coldstart(model_name):

    class Coldstart(models.Model):
        """represent default recommendation"""
        recomm_id = models.IntegerField(null=True,db_column='recommendation_id')
        content_recommended = models.CharField(max_length=50,null=True,db_column='content_id')
        confidence = models.FloatField(null=True,db_column='confidence')
        support = models.FloatField(null=True,db_column='support')
        id = models.AutoField(primary_key=True, null=False)

        def __str__(self):
            return str(self.content_recommended)+":"+str(self.confidence)
        def __hash__(self):
            return self.content_recommended.__hash__()

        def __eq__(self, other):
            return self.content_recommended == other.content_recommended

        @classmethod
        def get_content(cls,recomm_id=None):
            if not recomm_id:
                content = cls.objects.all().order_by('-confidence').values_list('content_recommended',flat=True)
                return list(content)
            content = cls.objects.filter(recomm_id=recomm_id).order_by('-confidence').values_list('content_recommended', flat=True)
            return list(content)

        class Meta:
            db_table = model_name.lower() if model_name else 'coldstart'
    return Coldstart


class Banner(models.Model):
    """represent content for Banner."""
    class Meta:
        db_table = 'banners'
    recomm_id = models.IntegerField(null=True,db_column='recommendation_id')
    content_recommended = models.CharField(max_length=50,null=True,db_column='content_id')
    confidence = models.FloatField(null=True,db_column='confidence')
    support = models.FloatField(null=True,db_column='support')
    id = models.AutoField(primary_key=True, null=False)


class ContentSeen(models.Model):
    """represent content seen deatils of User."""
    user_id = models.BigIntegerField(db_index=True)
    content_id = models.CharField(max_length=50)
    content_name = models.CharField(max_length=100,null=True)
    date = models.DateTimeField()
    mou = models.DecimalField(max_digits=8, decimal_places=3,db_index=True)
    id = models.AutoField(primary_key=True, null=False)
    def __str__(self):
        return str(self.mou)
    class Meta:
        db_table = 'user_streaming_history'


class ContentAll(models.Model):
    """represent Content details in db."""
    content_id   = models.CharField(max_length=50,primary_key=True,null=False,db_column='CONTENT_ID',db_index=True)
    content_name = models.CharField(max_length=200,db_column='PARENT_NAME',null=True)
    content_type = models.CharField(max_length=200,db_column='CONTENT_TYPE',null=True,db_index=True)
    circle       = models.CharField(max_length=50,db_column='CIRCLE',db_index=True)
    language     = models.CharField(max_length=200,db_column='LANGUAGE',null=True)

    # language = ListCharField(
    #     base_field=models.CharField(max_length=10, null=True,db_column='LANGUAGE'),
    #
    #     max_length=(6 * 11)  # 6 * 10 character nominals, plus commas
    # )

    mou          = models.DecimalField(null=True,max_digits=15,decimal_places=5,db_column='mou')
    mou_user     = models.DecimalField(null=True,max_digits=15,decimal_places=5,db_column='mou_user')
    partner      = models.CharField(max_length=200,db_column='PARTNER')
    uu_played    = models.IntegerField(null=True,db_column='UU_PLAYED')
    session      = models.IntegerField(null=True,db_column='SESSIONS')
    id           = models.AutoField(primary_key=True, null=False)

    class Meta:
        db_table='content_data'

class BannerContent(models.Model):
    """represent Content details in db."""
    content_id  = models.CharField(max_length=50,null=False,db_column='CONTENT_ID',db_index=True)
    recomm_id = models.IntegerField(null=True, db_column='recommendation_id')
    content_name= models.CharField(max_length=200,db_column='PARENT_NAME',null=True)
    content_type= models.CharField(max_length=200,db_column='CONTENT_TYPE',null=True,db_index=True)
    circle      = models.CharField(max_length=50,db_column='CIRCLE',db_index=True)
    language    = models.CharField(max_length=200,db_column='LANGUAGE',null=True)

    # language = ListCharField(
    #     base_field=models.CharField(max_length=10, null=True,db_column='LANGUAGE'),
    #
    #     max_length=(6 * 11)  # 6 * 10 character nominals, plus commas
    # )
    mou         = models.DecimalField(null=True,max_digits=15,decimal_places=5,db_column='mou')
    mou_user    = models.DecimalField(null=True,max_digits=15,decimal_places=5,db_column='mou_user')
    partner     = models.CharField(max_length=200,db_column='PARTNER')
    uu_played   = models.IntegerField(null=True,db_column='UU_PLAYED')
    session     = models.IntegerField(null=True,db_column='SESSIONS')
    id          = models.AutoField(primary_key=True, null=False)

    class Meta:
        db_table='banner_content'

class Content(models.Model):
    """Represents content detais for publish or unpublish"""
    content_id = models.CharField(max_length=100, primary_key=True, null=False, db_column='content_id', db_index=True)
    content_type = models.CharField(max_length=200, null=True, db_column='content_type')
    content_name = models.CharField(max_length=200, null=True, db_column='content_name')

    # genre = models.CharField(max_length=200, null=True)
    # actor = models.CharField(max_length=200, null=True)
    # language = models.CharField(max_length=200, null=True)

    duration = models.CharField(max_length=100, null=True)
    partner = models.CharField(max_length=200, null=True)

    language = ListCharField(
        base_field=models.CharField(max_length=10, null=True,db_column='language'),

        max_length=(6 * 11) # 6 * 10 character nominals, plus commas
    )
    genre = ListCharField(
        base_field=models.CharField(max_length=10, null=True, db_column='genre'),

        max_length=(6 * 11)  # 6 * 10 character nominals, plus commas
    )

    actor = ListCharField(
        base_field=models.CharField(max_length=10, null=True, db_column='actor'),

        max_length=(6 * 11) # 6 * 10 character nominals, plus commas

    )
    parent_id = models.CharField(max_length=200, null=True,db_column='content_parent_id')
    parent_name = models.CharField(max_length=200, null=True, db_column='partner_name')

    class Meta:
        db_table = 'content'

class Override(models.Model):
    id = models.AutoField(primary_key=True, null=False)
    action=models.CharField(max_length=30)
    recomm_id = models.IntegerField(null=True,db_column='recommendation_id')
    content_seen = models.IntegerField(null=True,db_column='content_seen')
    content_recommended = models.IntegerField(null=True,db_column='content_recommended')
    support_12 = models.FloatField(null=True,db_column='support_12')
    support_1 = models.FloatField(null=True,db_column='support_1')
    support_2 = models.FloatField(null=True,db_column='support_2')
    confidence = models.FloatField(null=True)
    lift = models.FloatField(null=True)

    class Meta:
        db_table='override'


class RecommendationAll(models.Model):
    id = models.AutoField(primary_key=True, null=False)
    user_id = models.BigIntegerField(db_index=True,null=True,db_column='user_id')
    content_id = models.CharField(max_length=50,null=True, db_column='content_id',db_index=True)
    #content_name = models.CharField(max_length=200, db_column='content_name', null=True)
    recomm_score = models.DecimalField(max_digits=15, decimal_places=5,null=True,db_column="rank")
    content_type = models.CharField(max_length=200, db_column='content_type', null=True)
    # release_year = models.IntegerField()
    director = models.CharField(max_length=100)
    actor = models.CharField(max_length=100)
    genre = models.CharField(max_length=20)
    language = models.CharField(max_length=100)

    #ratings      = models.IntegerField(default=None)
    class Meta:
        db_table='recommendations_all'


class UserAction(models.Model):
    # id = models.AutoField(primary_key=True, null=False)
    user_id = models.BigIntegerField(db_column='user_id',db_index=True)
    content_id = models.CharField(max_length=100)
    action_id = models.IntegerField(db_column='action_id',db_index=True)
    value = models.CharField(max_length=100, null=True)
    class Meta:
        db_table = 'user_action'