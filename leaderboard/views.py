from rest_framework import viewsets, permissions
from .models import LeaderboardEntry
from .serializers import LeaderboardEntrySerializer

class LeaderboardViewSet(viewsets.ModelViewSet):
    serializer_class = LeaderboardEntrySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = LeaderboardEntry.objects.all().order_by('-score')
        difficulty = self.request.query_params.get('difficulty')
        if difficulty:
            qs = qs.filter(difficulty=difficulty)
        return qs

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save()