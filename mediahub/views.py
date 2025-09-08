
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class UploadView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        f = request.FILES.get("file")
        kind = request.data.get("kind", "image")
        if not f: 
            return Response({"detail":"file required"}, status=400)
        from .models import MediaAsset
        m = MediaAsset.objects.create(owner=request.user, kind=kind, file=f)
        return Response({"id": m.id, "url": m.file.url})
