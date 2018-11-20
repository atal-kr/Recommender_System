from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField



from applications.recommendation.models import User, Recommendation, Content, Banner, ContentSeen, UserAction


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields='__all__'
        model=User



class ContentSeenSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('user_id','content_id','content_name','date','mou')
        model = ContentSeen


class ContentSerializer(serializers.ModelSerializer):
    language=serializers.ListField(child=serializers.CharField(),read_only=True)
    genre = serializers.ListField(child=serializers.CharField(),read_only=True)
    actor = serializers.ListField(child=serializers.CharField(),read_only=True)
    class Meta:
        model= Content
        fields = '__all__'


class ContentWriteSerializer(serializers.ModelSerializer):
    language=serializers.ListField(child=serializers.CharField())
    genre = serializers.ListField(child=serializers.CharField())
    actor = serializers.ListField(child=serializers.CharField())
    class Meta:
        model= Content
        fields = '__all__'

class LoginSerializer(serializers.Serializer):
    username =serializers.CharField(max_length=30)
    password =serializers.CharField(max_length=10)

    def validate(self, data):
        username=data.get('username')
        password=data.get('password')

        if username and password:
            user = authenticate(username=username,password=password)
            if user :
                if user.is_active:
                    data['user']= user
                else:
                    raise ValidationError("user is not active.")
            else:
                raise ValidationError("user name and password not matched")
        else:
            raise ValidationError("must provide user and password")
        return data



class RecommendationSerializer(serializers.ModelSerializer):
    recomm_id = serializers.CharField(required=False)
    content_seen = serializers.CharField(required=True)
    content_recommended =serializers.CharField(required=True)
    confidence = serializers.CharField(required=False)

    class Meta:
        fields = ('recomm_id','content_seen','content_recommended','confidence')
        model = Recommendation

    def delete(self):
        from applications.common.lib import filter_by_key
        obj = filter_by_key(Recommendation,**self.data)
        return obj.delete()

class UserActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAction
        fields='__all__'

