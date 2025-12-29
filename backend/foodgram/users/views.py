from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from rest_framework.response import Response

from .serializers import UserSerializer

User = get_user_model()


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

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
            return Response({'status': 'current password is incorrect'},
                            status=400)

        user.set_password(new_password)
        user.save()
        return Response({'status': 'password set'}, status=204)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = serializer.data
        data.pop('password', None)
        return Response(data, status=201, headers=headers)
