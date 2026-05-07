from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from django.shortcuts import get_object_or_404
from accounts.models import User
from .services import NotificationService
from .config import EVENTS

class NotificationDebugSendView(APIView):
    """
    DEBUG ONLY: Allows sending any notification to any user.
    Only accessible by admins.
    """
    permission_classes = [IsAdminUser]

    def post(self, request):
        user_id = request.data.get('user_id')
        event_type = request.data.get('event_type')
        context = request.data.get('context', {})

        if not user_id or not event_type:
            return Response(
                {'error': 'user_id and event_type are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if event_type not in EVENTS:
            return Response(
                {'error': f'Invalid event_type. Available: {list(EVENTS.keys())}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        recipient = get_object_or_404(User, id=user_id)
        
        NotificationService.notify(
            recipients=[recipient],
            event_type=event_type,
            context=context
        )

        return Response({'detail': f'Notification {event_type} sent to {recipient.username}'})

class NotificationDebugInfoView(APIView):
    """Returns users list ONLY for admin-led notification sending."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = User.objects.all().values('id', 'username', 'email')
        return Response({
            'users': list(users)
        })
