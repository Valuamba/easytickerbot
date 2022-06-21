from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class AccountView(APIView):
    def get(self, request: Request, format=None):
        return Response({"email": request.user.email, "role": request.user.role})
