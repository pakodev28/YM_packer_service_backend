from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CreateOrderSerializer


class CreateOrderAPIView(APIView):
    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save()
            return Response(
                {"order_id": order.pk}, status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
