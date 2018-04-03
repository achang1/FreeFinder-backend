from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.reverse import reverse

from profile.serializers import ProfileSerializer


class ProfileList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = ProfileSerializer

    def perform_create(self, serializer):
        serializer.save()


class ProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProfileSerializer

    def get_queryset(self):
        return User.objects.all().filter(username=self.request.user).select_related()

