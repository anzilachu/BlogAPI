from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.conf import settings
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken,AccessToken
from rest_framework_simplejwt.views import TokenObtainPairView
import requests
import logging

from .models import Author, Post
from .serializers import AuthorSerializer, PostSerializer

logger = logging.getLogger(__name__)

class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.action in ['create', 'list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user and not request.user.is_staff:
            return Response({
                'error': "You cannot edit this author profile."
            }, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user and not request.user.is_staff:
            return Response({
                'error': "You cannot delete this author profile."
            }, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        name = request.data.get('name')
        email = request.data.get('email')
        bio = request.data.get('bio', '')
        password = request.data.get('password')
        
        if not name or not email or not password:
            return Response({'error': 'Please provide name, email, and password'}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email=email).exists():
            return Response({'error': 'An author with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.create_user(username=email, email=email, password=password)
        author = Author.objects.create(user=user, name=name, email=email, bio=bio)
        
        return Response({
            'author_id': author.id,
            'name': author.name,
            'email': author.email
        }, status=status.HTTP_201_CREATED)

class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        
        user = authenticate(request, username=email, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        author = self.request.user.author
        location = self.request.data.get('location', '')

        if location:
            try:
                ola_api_url = f"https://api.olamaps.io/places/v1/autocomplete?input={location}&api_key={settings.OLA_MAPS_API_KEY}"
                response = requests.get(ola_api_url)
                response.raise_for_status()
                data = response.json()
                
                first_result = data.get('predictions', [])[0]
                latitude = first_result.get('geometry', {}).get('location', {}).get('lat')
                longitude = first_result.get('geometry', {}).get('location', {}).get('lng')
                
                if latitude and longitude:
                    serializer.save(author=author, location_lang=latitude, location_long=longitude)
                else:
                    logger.warning(f"No coordinates found for location: {location}")
                    serializer.save(author=author)
            except requests.RequestException as e:
                logger.error(f"Error fetching location data: {str(e)}")
                serializer.save(author=author)
            except (KeyError, IndexError) as e:
                logger.error(f"Error parsing location data: {str(e)}")
                serializer.save(author=author)
        else:
            serializer.save(author=author)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user.author:
            return Response({
                'error': f"You cannot edit this post. This is {instance.author.name}'s post."
            }, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user.author:
            return Response({
                'error': f"You cannot delete this post. This is {instance.author.name}'s post."
            }, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

