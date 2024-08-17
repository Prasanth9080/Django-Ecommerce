from django.urls import path
from . import views
from .views import custom_logout, remove_cart, minus_cart, plus_cart, CheckoutView, OrderSummaryView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_view
from .forms import LoginForm, MyPasswordResetForm, MyPasswordChangeForm, MySetPasswordForm 


urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('category/',views.CategoryView.as_view(),name='category'),
    path('category/<slug:value>/', views.CategoryView.as_view(), name='category'),  # Ensure this matches the URL you are accessing
    path('category/<value>', views.CategoryTitle.as_view(), name="category-title"),
    path('productdetail/<int:pk>', views.ProductDetail.as_view(), name="product-detail"),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('address/', views.address, name='address'),
    path('updateaddress/<int:pk>', views.updateAddress.as_view(), name='updateaddress'),

    #login authentication
    path('registration/', views.CustomerRegistrationView.as_view(), name="customerregistration"),
    path('accounts/login/', auth_view.LoginView.as_view(template_name='app/login.html', authentication_form=LoginForm), name='login'),
    path('passwordchange/', auth_view.PasswordChangeView.as_view(template_name='app/changepassword.html', form_class=MyPasswordChangeForm, success_url='/passwordchangedone'), name='passwordchange'),
    path('passwordchangedone/', auth_view.PasswordChangeDoneView.as_view(template_name='app/passwordchangedone.html'), name='passwordchangedone'),
    path('logout/', custom_logout, name='logout'),

    path('password-reset/', auth_view.PasswordResetView.as_view(template_name='app/password_reset.html', 
    form_class=MyPasswordResetForm), name="password_reset"),

    path('password-reset/done/', auth_view.PasswordResetDoneView.as_view(template_name='app/password_reset_done.html'),
    name='password_reset_done'),

    path('password-reset-confirm/<uidb64>/<token>/', auth_view.PasswordResetConfirmView.as_view
    (template_name='app/password_reset_confirm.html',
    form_class=MySetPasswordForm), name='password_reset_confirm'),

    path('password-reset-complete/', auth_view.PasswordResetCompleteView.as_view(template_name='app/password_reset_complete.html'),
     name='password_reset_complete'),

     #Add to Cart
     path('add-to-cart/', views.add_to_cart, name='add-to-cart'),
     path('cart/', views.show_cart, name='showcart'),
    #  path('success/', PaymentSuccessView.as_view(), name='payment_success'),
    #  path('cancel/', PaymentCancelView.as_view(), name='payment_cancel'),
    #  path('create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create_checkout_session'),
     path('order-summary/', OrderSummaryView.as_view(), name='order_summary'),
     path('checkout/', views.CheckoutView.as_view(), name='checkout'),
     path('pluscart/', views.plus_cart, name='pluscart'),
     path('minuscart/', views.minus_cart),
     path('removecart/', views.remove_cart),
     path('orders/', views.home, name='orders'),
    #  path('charge/', charge, name='charge')
    #  path('payment/', payment.as_view(), name='payment'),  # Use as_view() for class-based views

]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


