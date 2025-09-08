from rest_framework.generics import ListAPIView
from profiles.models import Profile
from rest_framework.serializers import ModelSerializer

class CardSerializer(ModelSerializer):
    class Meta:
        model = Profile
        fields = ("id","display_name","gender","seeking","location")

class DiscoverView(ListAPIView):
    serializer_class = CardSerializer
    def get_queryset(self):
        qs = Profile.objects.filter(is_visible=True)
        g = self.request.query_params.get("gender")
        s = self.request.query_params.get("seeking")
        if g: qs = qs.filter(gender__iexact=g)
        if s: qs = qs.filter(seeking__iexact=s)
        return qs.order_by("-id")
