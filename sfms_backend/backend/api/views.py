from django.contrib.auth import login, logout
from django.core import serializers

from .models import Payment, Program, Student, Term

from .serializers import PaymentSerializer
from .serializers import TermSerializer
from .serializers import StudentSerializer
from .serializers import ProgramSerializer
from .serializers import LoginSerializer
from .serializers import UserSerializer

from django.contrib.auth.models import User

from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework import views, viewsets
from rest_framework.response import Response
from django.http import Http404
from rest_framework.decorators import api_view

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework.authentication import TokenAuthentication

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests
from django.shortcuts import render

#from .external_api_handler import Handler


# Create your views here.
#@method_decorator(csrf_exempt, name='dispatch')
class PaymentView(views.APIView):
    authentication_classes = (TokenAuthentication,)

    def get(self, request, format=None):
        """ List all payments"""
        payments = Payment.objects.all()
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)
    
    def post(self, request, format=None):
        from .external_api_handler import APIHandler
        """Create a new payment"""

        # get request data
        partyId = request.GET.get('partyId', '')
        externalId = request.GET.get('externalId', '')
        amount = str(self.request.data['amount'])

        # Query external API handlers
        pay = APIHandler()
        pay.get_uuid()
        pay.create_api_user()
        pay.get_api_key()
        pay.get_api_token()

        try:
            serializer = PaymentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                payer = pay.request_to_pay(amount, partyId,
                externalId)
                        
                if payer.status_code == 202:                  

                    # set variables
                    s_pk = int(self.request.data['student'])
                    t_pk = int(self.request.data['term'])
                    student = str(User.objects.get(pk=s_pk))
                    term = str(Term.objects.get(pk=t_pk))
                                                                    
                    content = {'student': student,
                    'amount': amount,
                    'account':partyId,
                    'reference':externalId,
                    'term': term
                    }
                    
                    return Response(content,
                        status=status.HTTP_201_CREATED)
                    return Response(status=status.HTTP_400_BAD_REQUEST)
                elif payer.status_code == 400:
                    raise ValueError('BAD REQUEST TO API')
                elif payer.status_code == 409:
                    raise TypeError('RESOURCE ALREADY EXITS')
                elif payer.status_code == 500:
                    raise TypeError('INTERNAL SERVER ERROR')
                elif payer.status_code == 403:
                    raise TypeError('EXCEEDED')
        except Exception as e:
            return Response({'Error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        error = pay.request_to_pay(amount, partyId,
                externalId)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class StudentView(viewsets.ModelViewSet):
    serializer_class = StudentSerializer
    queryset = Student.objects.all()
  

class TermView(viewsets.ModelViewSet):
    serializer_class = TermSerializer
    queryset = Term.objects.all()

class ProgramView(viewsets.ModelViewSet):
    serializer_class = ProgramSerializer
    queryset = Program.objects.all()


class LoginView(views.APIView):
    # This view should be accessible also for unauthenticated users.
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        """POST request to get session Cookies:
            csrf and sessionid
        """
        serializer = LoginSerializer(
            data=self.request.data,
            context={ 'request': self.request }
            )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return Response(None, status=status.HTTP_202_ACCEPTED)

class LogoutView(views.APIView):
    """" Logs out the currecnt signed in user"""

    def get(self, request, format=None):
        """GET request to flash user cookies and log them out"""
        logout(request)
        return Response(status=status.HTTP_200_OK)

class ProfileView(generics.RetrieveAPIView):
    """Returns the profile of the user"""
    serializer_class = UserSerializer

    def get_object(self):
        """ GET the user object"""
        return self.request.user




