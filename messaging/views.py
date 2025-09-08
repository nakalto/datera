from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .models import Message
from .services import get_or_create_thread, can_send

User = get_user_model()

def entitled_to_chat(user):
    return False  # TODO: integrate payments

class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, user_id):
        other = User.objects.get(id=user_id)
        if other.id == request.user.id:
            return Response({"detail":"cannot DM yourself"}, status=400)
        thread = get_or_create_thread(request.user, other)
        ok = can_send(request.user, thread, entitled_to_chat(request.user))
        if not ok:
            return Response({"paywall": True, "detail": "Activate access to continue"}, status=402)
        body = (request.data.get("body") or "").strip()
        if not body:
            return Response({"detail":"message required"}, status=400)
        msg = Message.objects.create(thread=thread, sender=request.user, body=body)
        flag = "a_first_free_used" if thread.a_id == request.user.id else "b_first_free_used"
        if getattr(thread, flag) is False:
            setattr(thread, flag, True); thread.save(update_fields=[flag])
        return Response({"id": msg.id, "created_at": msg.created_at, "body": msg.body}, status=201)
