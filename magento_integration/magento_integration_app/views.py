from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status,generics
from django.contrib.auth import authenticate, login, logout
from .serializers import UserSerializer ,ProductSerializer,CartItemSerializer,CustomUserSerializer,CustomerSerializer,CartSerializer
from django.utils.crypto import get_random_string
from .models import Customer,Product,Cart,CartItem,CustomUser
from django.contrib import messages
from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from django_tables2.views import SingleTableView
from .tables import ProductTable
from django.contrib.sessions.models import Session
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes,authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from rest_framework.authentication import SessionAuthentication
import json



#widok testowy dashboarda'a, wykresy itd
class DashboardView(TemplateView):
    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Pobierz dane dotyczące ilości produktów z magazynu
        stock_data = Product.objects.values('name', 'stock_quantity')

        context['stock_data_json'] = json.dumps(list(stock_data))
        return context



#widok ogolny api, z informacjami o wszystkich url i dostepu do nich
@api_view(['GET'])
def ApiOverview(request):
    api_urls = {
        'get_all_from_custom_user': 'custom_user/get_many_user/',
        'get_all_items_from_cart': 'cart/get_many_items',
        'get_one_item_from_cart' : 'cart/get_item/<int:item_id>/',
        'add_item_to_cart': 'add_to_cart/',
        'create_item': 'cart/post/',
        'update_item_in_cart': 'cart/put/<int:item_id>/',
        'delete_item_in_cart': 'remove-from-cart/<int:item_id>/'
    }

    return Response(api_urls)

#widok zwracajacy wszystkie produkty
class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    def get_queryset(self):
        queryset = Product.objects.all()

        # Jeśli przekazane jest Magento SKU w parametrze żądania
        magento_sku = self.request.query_params.get('magento_sku')
        if magento_sku:
            queryset = queryset.filter(magento_sku=magento_sku)

        return queryset
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        # Renderowanie szablonu
        return render(request, 'product_list.html', {'products': serializer.data})

#widok odpowiadajacy za szczegoly interesujacego nas produktu
class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    template_name = 'product_detail.html'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return render(request, self.template_name, {'product': serializer.data})

# widok dodawania produktow do koszyka
class AddToCartView(generics.CreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartItemSerializer

    def post(self, request, *args, **kwargs):
        product_magento_sku = request.data.get('magento_sku')
        quantity = request.data.get('quantity')

        if not product_magento_sku:
            return Response({'error': 'Pole "magento_sku" jest wymagane.'}, status=status.HTTP_400_BAD_REQUEST)
        if not quantity:
            return Response({'error': 'Pole "quantity" jest wymagane.'}, status=status.HTTP_400_BAD_REQUEST)

        # Sprawdzenie, czy produkt istnieje
        try:
            product = Product.objects.get(magento_sku=product_magento_sku)
        except Product.DoesNotExist:
            return Response({'error': 'Podany produkt nie istnieje.'}, status=status.HTTP_400_BAD_REQUEST)

        # Sprawdzenie, czy ilość produktu w magazynie nie wynosi zero
        if product.stock_quantity == 0:
            return Response({'error': 'Wybranego produktu nie ma w magazynie.'}, status=status.HTTP_400_BAD_REQUEST)

        # Sprawdzenie, czy istnieje aktywna sesja
        session_key = request.session.session_key
        if not session_key:
            # Twórz nową sesję
            request.session.create()
            session_key = request.session.session_key

        # Sprawdzenie, czy istnieje koszyk powiązany z daną sesją i klientem
        customer = Customer.objects.get(user=request.user)
        cart, created = Cart.objects.get_or_create(customer=customer, session_id=session_key)

        # Dodawanie produktu do koszyka
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        # Zaktualizowanie ilości produktu w koszyku
        cart_item.quantity += int(quantity)
        cart_item.save()

        return Response({'success': 'Produkt został dodany do koszyka.'}, status=status.HTTP_201_CREATED)

class RegistrationView(APIView):
    def get(self,request):
        return render(request,'register.html')

    def post(self, request):
        print(request.data)
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            try:
                customer = Customer.objects.get_object_or_create(user=user, magento_sku=get_random_string(length=10))
                messages.success(request, 'Konto zostało poprawnie utworzone. Możesz się teraz zalogować.')
                return JsonResponse({'success': True, 'message': 'Konto zostało poprawnie utworzone.'})
            except Exception as e:
                return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#widok do logowania(jeszcze trzeba dodac poprawki, na szybko)
class LoginView(APIView):
    def get(self,request):
        return render(request,'login.html')
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

#widok do wylogowania
class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_200_OK)

#widok koszyka danego klienta oraz produktow, ktore do niego dodal


class CartView(generics.ListCreateAPIView):
    serializer_class = CartSerializer

    def get_queryset(self):
        customer_id = self.kwargs.get('customer_id')

        if customer_id:
            return Cart.objects.filter(customer__magento_sku=customer_id)
        else:
            return Cart.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        # Renderowanie szablonu
        return render(request, 'cart.html', {'cart_items': serializer.data})


class CartDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    lookup_field = 'cart_id'


"""CRUD metoda oparta na klasach
pojedynczy klient,
wielu klientów,
dodawanie nowego klienta
GET,POST"""
class CustomerView(generics.ListCreateAPIView):
    serializer_class = CustomerSerializer

    def get_queryset(self):
        magento_sku = self.kwargs.get('magento_sku')
        if magento_sku:
            return Customer.objects.filter(magento_sku=magento_sku)
        else:
            return Customer.objects.all()

"""Aktualizacja klienta,
Usuwanie kleinta, z wykorzystaniem pola CARD_ID
PUT, RETRIVE,PATCH"""
class CustomerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    lookup_field = 'magento_sku'

"""CRUD metoda oparta na klasach
pojedynczy produkt,
wiele produktów,
dodawanie nowego produktu
GET,POST"""

class ProductView(generics.ListCreateAPIView):

    serializer_class = ProductSerializer
    def get_queryset(self):
        magento_sku = self.kwargs.get('magento_sku')
        if magento_sku:
            return Product.objects.filter(magento_sku=magento_sku)
        else:
            return Product.objects.all()


"""Aktualizacja produktu,
Usuwanie produktu, z wykorzystaniem pola MAGENTO_SKU
PUT, RETRIVE,PATCH"""
class ProductDetailView_1(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'magento_sku'






"""CRUD metoda oparta na klasach
pojedynczy obiekt_w_koszyku,
wiele obiektów,
dodawanie nowego obiektu
GET,POST"""
class CartItemView(generics.ListCreateAPIView):
    serializer_class = CartItemSerializer

    def get_queryset(self):
        cart_id = self.kwargs.get('cart_id')
        print(cart_id)
        if cart_id:
            return CartItem.objects.filter(id=cart_id)
        else:
            return CartItem.objects.all()


"""Aktualizacja obiektu,
Usuwanie obiektu, z wykorzystaniem pola CARD_ID
PUT, RETRIVE,PATCH"""
class CartItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    lookup_field = 'cart_id'



#Pobieranie wszystkich przedmiotow w koszyku uzytkownika
@api_view(['GET'])
def get_cart_items(request):
    cart_items = CartItem.objects.all()
    serializer = CartItemSerializer(cart_items, many=True)
    return Response(serializer.data)

#Pobieranie pojedynczego przedmiotu w koszyku uzytkownika
@api_view(['GET'])
def get_cart_item(request, item_id):
    cart_item = CartItem.objects.get(id=item_id)
    serializer = CartItemSerializer(cart_item)
    return Response(serializer.data)

#Tworzenie nowego przedmiotu w koszyku
@api_view(['POST'])

def create_cart_item(request):
    serializer = CartItemSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#Aktualizacja przedmiotu w koszyku

@api_view(['PUT'])
def update_cart_item(request, id):
    cart_item = CartItem.objects.get(id=id)
    serializer = CartItemSerializer(cart_item, data=request.PUT)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#Usuwanie przedmiotu z koszyka:
@api_view(['DELETE'])
def delete_items(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id)
    item.delete()
    return Response(status=status.HTTP_202_ACCEPTED)


"""CRUD metoda oparta na klasach
pojedynczy obiekt_w_koszyku,
wiele obiektów,
dodawanie nowego obiektu
GET,POST"""
class CustomUserView(generics.ListCreateAPIView):
    serializer_class = CustomUserSerializer

    def get_queryset(self):
        id = self.kwargs.get('id')
        if id:
            return CustomUser.objects.filter(id=id)
        else:
            return CustomUser.objects.all()

"""Aktualizacja obiektu,
Usuwanie obiektu, z wykorzystaniem pola CARD_ID
PUT, RETRIVE,PATCH"""
class CustomUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    lookup_field = 'id'

"""CRUD metoda oparta na klasach
pojedynczy klient,
wielu klientów,
dodawanie nowego klienta
GET,POST"""
class CustomerView(generics.ListCreateAPIView):
    serializer_class = CustomerSerializer

    def get_queryset(self):
        magento_sku = self.kwargs.get('magento_sku')
        if magento_sku:
            return Customer.objects.filter(magento_sku=magento_sku)
        else:
            return Customer.objects.all()

"""Aktualizacja klienta,
Usuwanie kleinta, z wykorzystaniem pola CARD_ID
PUT, RETRIVE,PATCH"""
class CustomerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    lookup_field = 'magento_sku'

class BaseView(TemplateView):
    template_name = 'base.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user if self.request.user.is_authenticated else None
        return context
