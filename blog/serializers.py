from rest_framework import serializers
from .models import Author, Post
from django.contrib.auth.models import User


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name', 'email', 'bio']

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'created_at', 'location_lang', 'location_long', 'author']
        read_only_fields = ['author', 'location_lang', 'location_long']

