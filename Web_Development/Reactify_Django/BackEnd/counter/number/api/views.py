from .serializer import CounterSerializer
from ..models import Counter
from rest_framework import viewsets


class CounterViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing Counter instances.
    """
    serializer_class = CounterSerializer
    queryset = Counter.objects.all()

    # End
