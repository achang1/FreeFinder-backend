from rest_framework import serializers
from profile.models import Profile
from django.contrib.auth.models import User

class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    # todos = serializers.HyperlinkedRelatedField(
    #     many=True,
    #     view_name='todos:todo-detail',
    #     read_only=True
    # )
    password = serializers.CharField(write_only=True)
    location = serializers.SerializerMethodField()
    email = serializers.CharField(required=True)
    def create(self, validated_data):
        user = User(
            username=validated_data.get('username', None),
            email=validated_data.get('email', None),
            first_name=validated_data.get('first_name', None),
            last_name=validated_data.get('last_name', None),
        )
        user.set_password(validated_data.get('password', None))
        user.save()
        user.profile.location = validated_data.get('location', None)
        user.save()
        return user

    def update(self, instance, validated_data):
        for field in validated_data:
            if field == 'password':
                instance.set_password(validated_data.get(field))
            else:
                instance.__setattr__(field, validated_data.get(field))
        instance.save()
        return instance

    def get_location(self, instance):
        return instance.profile.location

    class Meta:
        model = User
        fields = ('url', 'id', 'username',
                  'password', 'first_name', 'last_name',
                  'email', 'location',
                  )
        extra_kwargs = {
            'url': {
                'view_name': 'profile:profile-detail',
            }
        }