from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission,User
from django.contrib.sessions.models import Session

#model przydzielania uprawnien, uzytkownikowi
class CustomUser(AbstractUser):
    groups = models.ManyToManyField(Group, related_name='customuser_set')
    user_permissions = models.ManyToManyField(Permission, related_name='customuser_set')

#model przechowujacy dane klienta zarejestrowanego(oczywiście do rozwinięcia)
class Customer(models.Model):
    magento_sku = models.CharField(max_length=100, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    date_deleted = models.DateTimeField(null=True, blank=True)
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    is_subscribed = models.BooleanField(default=False)

    # Zwracane pole, które uważasz za ważne

    def __str__(self):
        return self.magento_sku

#model Kategorii danego produktu znajdującego sie w sklepie
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# model produktu i atrybutu z nim związane
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    magento_sku = models.CharField(max_length=100)
    size = models.CharField(max_length=50)
    available = models.BooleanField(default=True)
    stock_quantity = models.IntegerField(default=0)

    def __str__(self):
        return self.name
#funkcja sprawdzajaca dostepnosc produktu
    def update_availability(self):
        self.available = self.stock_quantity > 0
        self.save()

#model Koszyka powiązany z klientem, produktami i sesja
# (do obsłuzenia, w tym momencie po wyczerpaniu czasu zdefiniowanego w settingsach przy użyciu firebase'a,
# uzytkownik zostaje wylogowany z platoformy, a trzeba zmienic to na usuwanie automatyczne produktów
# z koszyka)
class Cart(models.Model):
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='CartItem')
    session = models.ForeignKey(Session, null=True, blank=True, on_delete=models.SET_NULL)

#funkcja obliczajaca sume produktow znajdujacych sie w koszyku klienta, zgodnie z iloscia danego produktu i jego ceny

    def calculate_total_price(self):
        total_price = 0
        cart_items = CartItem.objects.filter(cart=self)
        for item in cart_items:
            total_price += item.product.price * item.quantity
        return total_price

    def __str__(self):
        return f"Cart - {self.customer.user.username} - {self.calculate_total_price()}"
#model odpowiadajacy za produkty dodane do koszyka)
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return f"CartItem - {self.product.name} - Quantity: {self.quantity}"


