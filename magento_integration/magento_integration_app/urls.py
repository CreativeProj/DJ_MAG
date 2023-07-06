from django.urls import path
from .views import ApiOverview,RegistrationView,LoginView,ProductListView,ProductDetailView,\
    AddToCartView,CartView,CartItemView,CartItemDetailView,DashboardView,ProductView,ProductDetailView_1,\
    get_cart_items,get_cart_item,create_cart_item,update_cart_item,delete_items,\
    CustomUserView,CustomUserDetailView,\
    CustomerView,CustomerDetailView,\
    CartView,CartDetailView,CartItem,BaseView
from rest_framework.authtoken.views import obtain_auth_token

app_name = 'magento_integration_app'

urlpatterns = [
    #url crud w drf'ie dla produktow
    path('products/items/', ProductView.as_view(), name='products'),
    path('products/items/get/<str:magento_sku>/', ProductView.as_view(), name='products-item'),
    path('products/items/update/<str:magento_sku>/', ProductDetailView_1.as_view(), name='update-product'),
    path('products/items/delete/<str:magento_sku>/', ProductDetailView_1.as_view(), name='delete-product'),

    #url crud w drf'ie dla modelu CustomUser(klasyfikacja, przydzielanie uprawnien zgodnie z grupa)
    path('user/permission/', CustomUserView.as_view(), name='users_permission'),
    path('user/permission/get/<int:id>/', CustomUserView.as_view(), name='user_permission'),
    path('user/permission/update/<int:id>/', CustomUserDetailView.as_view(), name='update-user_permission'),
    path('user/permission/delete/<int:id>/', CustomUserDetailView.as_view(), name='delete-user_permission'),

    #url crud w drf'ie dla modelu Customer
    path('customer/customers/', CustomerView.as_view(), name='customers'),
    path('customer/customers/get/<str:magento_sku>/', CustomerView.as_view(), name='customer'),
    path('customer/customers/update/<str:magento_sku>/', CustomerDetailView.as_view(), name='update-customer'),
    path('customer/customers/delete/<str:magento_sku>/', CustomerDetailView.as_view(), name='delete-customer'),

    #url rejestracja oraz logowanie
    path('api/register/', RegistrationView.as_view(), name='api-register'),
    path('api/login/', LoginView.as_view(), name='api-login'),

    #widoki pomocnicze(tesotwanie)
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    #dodwanie produktu do koszyka
    path('add_to_cart/', AddToCartView.as_view(), name='add-to-cart'),

    #url crud w drf'ie dla modelu Cart
    path('cart/items/', CartView.as_view(), name='carts'),
    path('cart/items/get/<int:customer_id>/', CartView.as_view(), name='cart'),
    path('cart/items/update/<int:cart_id>/', CartDetailView.as_view(), name='update-cart'),
    path('cart/items/delete/<int:cart_id>/', CartDetailView.as_view(), name='delete-cart'),


    #url crud w drf'ie dla modelu CartItem
    path('cart_item/items/', CartItemView.as_view(), name='cart-items'),
    path('cart_items/items/get/<int:cart_id>/', CartItemView.as_view(), name='cart-item'),
    path('cart_items/items/update/<int:cart_id>/', CartItemDetailView.as_view(), name='update-cart-item'),
    path('cart_items/items/delete/<int:cart_id>/', CartItemDetailView.as_view(), name='delete-cart-item'),

    #url zastepcze, crud w drf'ie opraty na funkcjach
    path('cart/items2/', get_cart_items, name='get-cart-items'),
    path('cart/items2/<int:item_id>/', get_cart_item, name='f_get-cart-item'),
    path('cart/items2/create/', create_cart_item, name='f_create-cart-item'),
    path('cart/items2/update/<int:id>/', update_cart_item, name='f_update-cart-item'),
    path('cart/items2/delete/<int:id>/', delete_items, name='f_delete-cart-item'),

    #ogolny panel api
    #widoki odpowiadajace za uwierzytelnienie api
    #widok dashboarda -test wykresow
    path('api/panel/', ApiOverview, name='home'),
    path('api-token-auth/', obtain_auth_token, name='api-token-auth'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('', BaseView.as_view(), name='base'),

]