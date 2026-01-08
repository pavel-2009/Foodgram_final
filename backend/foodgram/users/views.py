from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from .serializers import UserSerializer
from .pagination import PageLimitPagination

User = get_user_model()


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    pagination_class = PageLimitPagination

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        user = request.user
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='set_password',
            permission_classes=[IsAuthenticated])
    def set_password(self, request):
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')

        user = request.user
        if not user.check_password(current_password):
            return Response({'current_password': 'Wrong password.'},
                            status=400)

        user.set_password(new_password)
        user.save()
        return Response({'status': 'password set'}, status=204)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated]) # noqa
    def subscriptions(self, request):
        user = request.user
        subscriptions = User.objects.filter(
            subscribed_users__user=user
        )
        page = self.paginate_queryset(subscriptions)
        if page is not None:
            serializer = UserSerializer(
                page,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = UserSerializer(
            subscriptions,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])  # noqa
    def subscribe(self, request, pk=None):
        user = request.user
        to_subscribe = self.get_object()

        if request.method == 'DELETE':
            if not user.subscriptions.filter(subscriptions=to_subscribe).exists():  # noqa
                return Response({'error': 'You are not subscribed to this user.'},  # noqa
                                status=400)
            user.subscriptions.filter(subscriptions=to_subscribe).delete()
            return Response(status=204)

        if user == to_subscribe:  # noqa
            return Response({'error': 'You cannot subscribe to yourself.'},
                            status=400)

        if user.subscriptions.filter(subscriptions=to_subscribe).exists():
            return Response({'error': 'You are already subscribed to this user.'},  # noqa
                            status=400)

        user.subscriptions.get_or_create(subscriptions=to_subscribe)
        serializer = UserSerializer(
            to_subscribe,
            context={'request': request}
        )
        return Response(serializer.data, status=201)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = serializer.data
        data.pop('password', None)
        return Response(data, status=201, headers=headers)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')
    try:
        user = User.objects.get(email=email)
        if not user.check_password(password):
            return Response({'error': 'Invalid credentials'}, status=400)
    except User.DoesNotExist:
        return Response({'error': 'Invalid credentials'}, status=400)

    token, created = Token.objects.get_or_create(user=user)
    return Response({'auth_token': token.key})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    request.auth.delete()
    return Response(status=204)
