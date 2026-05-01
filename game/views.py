from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import GameSession
from .serializers import GameSessionSerializer

class GameSessionViewSet(viewsets.ModelViewSet):
    serializer_class = GameSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return GameSession.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def latest(self, request):
        session = self.get_queryset().first()
        if session:
            return Response(self.get_serializer(session).data)
        return Response({'detail': 'Сохранений не найдено'}, status=status.HTTP_404_NOT_FOUND)