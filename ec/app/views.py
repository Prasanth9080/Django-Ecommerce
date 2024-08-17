from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from .models import Product, Customer, Cart, CarouselImage
from django.db.models import Count
from .forms import CustomerRegistrationForm
from django.contrib import messages
from .forms import CustomerProfileForm
from django.contrib.auth import logout
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET
import logging
import razorpay
from django.conf import settings
import stripe
from django.views.decorators.csrf import csrf_exempt
from stripe.error import CardError, RateLimitError, InvalidRequestError, AuthenticationError, APIConnectionError, StripeError
from django.contrib.auth.decorators import login_required
from django import forms


stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.
def home(request):
    items = CarouselImage.objects.all()  # Retrieve all CarouselImage objects
    return render(request, "app/home.html", {'items': items})  # Pass 'items' to the template

def about(request):
    return render(request, "app/about.html")

def contact(request):
    return render(request, "app/contact.html")

class CategoryView(View):
    def get(self,request,value):
        # Use the `value` parameter here as needed
        product = Product.objects.filter(category=value)
        title = Product.objects.filter(category=value).values('title')
        CATEGORY_CHOICES = Product.objects.filter(category=value)
        context = {
            'product': product,
            'title': title,
            'category_choices': CATEGORY_CHOICES,  # Add CATEGORY_CHOICES to the context
        }
        # context = {'value': value}  # Add `value` to the context dictionary
        return render(request,"app/category.html",locals())

class CategoryTitle(View):
    def get(self,request,value):
        product = Product.objects.filter(title=value)
        title = Product.objects.filter(category=product[0].category).values('title')
        return render(request, "app/category.html",locals())

class ProductDetail(View):
    def get(self,request,pk):
        product = Product.objects.get(pk=pk)
        return render(request,"app/productdetail.html",locals())

#Username, password
class CustomerRegistrationView(View):
    def get(self,request):
        form = CustomerRegistrationForm()
        return render(request, 'app/customerregistration.html',locals())
    def post(self,request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"congratulations! User Registration Successfully")
        else:
            messages.warning(request,"Invalid Input Data")
        return render(request, 'app/customerregistration.html',locals())

#carousel
# def carousel_view(request):
#     items = CarouselItem.objects.all()
#     return render(request, 'home.html', {'items': items})

class ProfileView(View):
    def get(self,request):
        form = CustomerProfileForm()
        return render(request, 'app/profile.html', {'form': form})
        
    def post(self,request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            mobile = form.cleaned_data['mobile']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']

            reg = Customer(user=user,name=name,locality=locality,mobile=mobile,city=city,state=state,zipcode=zipcode)
            reg.save()
            messages.success(request, "Data Saved Successfully!")
            return redirect('profile')
        else:
            messages.warning(request, "Invalid Input Data")

        return render(request, 'app/profile.html', {'form': form})

def address(request):
    add = Customer.objects.filter(user=request.user)
    return render(request, 'app/address.html',locals())

def custom_logout(request):
    logout(request)
    return redirect('login')

class updateAddress(View):
    def get(self,request,pk):
        add = Customer.objects.get(pk=pk)
        form = CustomerProfileForm(instance=add)
        return render(request, 'app/updateAddress.html',locals())

    def post(self,request,pk):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            add = Customer.objects.get(pk=pk)
            add.name = form.cleaned_data['name']
            add.locality = form.cleaned_data['locality']
            add.city = form.cleaned_data['city']
            add.mobile = form.cleaned_data['mobile']
            add.state = form.cleaned_data['state']
            add.zipcode = form.cleaned_data['zipcode']
            add.save()
            messages.success(request, "Data Saved Successfully")
        else:
            messages.warning(request, "Invalid Input Data")
        return redirect("address")


#Add to cart
# def add_to_cart(request):
#     user=request.user
#     product_id=request.GET.get('prod_id')
#     product = Product.objects.get(id=product_id)
#     Cart(user=user,product=product).save()
#     return redirect("/cart")

logger = logging.getLogger(__name__)

def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    
    # Log the product ID for debugging
    logger.debug(f"Product ID received: {product_id}")
    
    # Get the product, or raise a 404 error if not found
    product = get_object_or_404(Product, id=product_id)
    
    # Check if the product is already in the cart
    cart_item, created = Cart.objects.get_or_create(user=user, product=product)
    
    if created:
        logger.debug(f"Created new cart item for product ID: {product_id}")
    else:
        # If the item was found (i.e., not created), update the quantity
        logger.debug(f"Found existing cart item for product ID: {product_id}")
        cart_item.quantity += 1
        cart_item.save()

    # Redirect to the cart page
    return redirect("/cart")

def show_cart(request):
    user = request.user
    cart = Cart.objects.filter(user=user)

    amount = 0
    total_quantity = 0

    for p in cart: 
        value = p.quantity * p.product.discount_price
        amount += value
        total_quantity += p.quantity 

    shipping_price = total_quantity * 10
    totalamount = amount + shipping_price

    context = {
        'cart': cart,
        'amount': amount,
        'shipping_price': shipping_price,
        'totalamount': totalamount
    }
    
    return render(request, 'app/addtocart.html',locals())


# checkout-section-view

class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        YOUR_DOMAIN = "http://localhost:8000"

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Your Product Name',
                        },
                        'unit_amount': 1000,  # Amount in cents
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=YOUR_DOMAIN + '/success/',
            cancel_url=YOUR_DOMAIN + '/cancel/',
        )

        return redirect(checkout_session.url, code=303)


#Order summary

class OrderSummaryView(View):
    def get(self, request, *args, **kwargs):
        user = request.user
        addresses = Customer.objects.filter(user=user)
        cart_items = Cart.objects.filter(user=user)

        amount = 0
        total_quantity = 0

        for p in cart_items:
            value = p.quantity * p.product.discount_price
            amount += value
            total_quantity += p.quantity

        shipping_price = total_quantity * 10
        totalamount = amount + shipping_price

        context = {
            'cart_items': cart_items,
            'addresses': addresses,
            'totalamount': totalamount,
            'shipping_price': shipping_price,
            'amount': amount,
            'stripe_public_key': settings.STRIPE_PUBLISHABLE_KEY,
            'key': settings.STRIPE_PUBLISHABLE_KEY
        }
        
        return render(request, 'app/checkout.html', context)



#Checkout view

class CheckoutView(View):    
    def get(self, request, *args, **kwargs):
        user = request.user
        addresses = Customer.objects.filter(user=user)
        cart_items = Cart.objects.filter(user=user)

        amount = 0
        total_quantity = 0

        for p in cart_items:
            value = p.quantity * p.product.discount_price
            amount += value
            total_quantity += p.quantity

        shipping_price = total_quantity * 10
        totalamount = amount + shipping_price

        context = {
            'cart_items': cart_items,
            'addresses': addresses,
            'totalamount': totalamount,
            'shipping_price': shipping_price,
            'amount': amount,
            'stripe_public_key': settings.STRIPE_PUBLISHABLE_KEY,
            'key': settings.STRIPE_PUBLISHABLE_KEY
        }

        return render(request, 'app/checkout.html', context)

        
def charge(request):
    if request.method == 'POST': 
        charge = stripe.Charge.create(
            amount=500,
            currency='inr',
            description='Django',
            source=request.POST['stripeToken']
        )
        return render(request, 'checkout.html')
    return render(request, "app/test.html")

#checkout place_order

@login_required
def checkout(request):
    if request.method == 'POST':
        product = request.POST.get('product')
        quantity = request.POST.get('quantity')
        price = request.POST.get('price')
        user = request.user

        # Validate form data
        if not product or not quantity or not price:
            messages.error(request, 'Please fill in all fields.')
            return redirect('checkout')  # Redirect back to the checkout page

        # Create and save the order
        try:
            Order.objects.create(
                user=user,
                product=product,
                quantity=int(quantity),
                price=float(price)
            )
            messages.success(request, 'Order placed successfully!')
        except Exception as e:
            messages.error(request, f'Error placing order: {e}')

        return redirect('order_success')  # Redirect to a success page or another view

    # Handle GET request
    cart_items = ...  # Retrieve cart items
    addresses = ...  # Retrieve user addresses
    totalamount = ...  # Calculate total amount
    shipping_price = ...  # Calculate shipping price
    key = ...  # Stripe publishable key

    context = {
        'cart_items': cart_items,
        'addresses': addresses,
        'totalamount': totalamount,
        'shipping_price': shipping_price,
        'key': key,
    }
    return render(request, 'checkout.html', context)

#Place Order checkout

class checkout(View):

    def get(self, request):
        user = request.user
        addresses = Customer.objects.filter(user=user)
        cart_items = Cart.objects.filter(user=user)

        amount=0
        total_quantity = 0

        for p in cart_items:
            value = p.quantity * p.product.discount_price
            amount += value
            total_quantity += p.quantity

        shipping_price = total_quantity * 10
        totalamount = amount + shipping_price  # Set the total amount according to your logic
        totalprice = totalamount - shipping_price

        # razoramount = int(totalamount * 100)
        # client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SUCCESS))
        # data = { "amount": razoramount, "currency": "INR", "receipt": "order_rcptid_12" }
        # payment_response = client.order.create(data=data)
        # print(payment_response)

        return render(request, 'app/checkout.html', {
            'cart_items': cart_items,
            'addresses': addresses,
            'totalamount': totalamount, 
            'shipping_price': shipping_price, 
            'totalprice': totalprice,
            
            })


def plus_cart(request):
    if request.method == 'GET':
        prod_id =request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity+=1
        c.save()

        user = request.user
        cart = Cart.objects.filter(user=user)

        amount = 0
        total_quantity = 1
        for p in cart:
            value = p.quantity * p.product.discount_price
            amount += value
            total_quantity += p.quantity

        shipping_price = total_quantity * 10
        totalamount = amount + shipping_price


        data = {
            'quantity':c.quantity,
            'amount':amount,
            'totalamount':totalamount
        }
        return JsonResponse(data)


def minus_cart(request):
    if request.method == 'GET':
        prod_id=request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity-=1
        c.save()

        user = request.user
        cart = Cart.objects.filter(user=user)

        amount = 0
        total_quantity = 1
        for p in cart:
            value = p.quantity * p.product.discount_price
            amount += value
            total_quantity -= p.quantity

        shipping_price = total_quantity * 10
        totalamount = amount - shipping_price

        data = {
            'quantity':c.quantity,
            'amount':amount,
            'totalamount':totalamount
        }
        return JsonResponse(data)



def remove_cart(request):
    if request.method == 'GET':
        prod_id=request.GET['prod_id']
        Cart.objects.filter(Q(product=prod_id) & Q(user=request.user)).delete()

        user = request.user
        cart = Cart.objects.filter(user=user)

        amount = 0
        total_quantity = 1

        for p in cart:
            value = p.quantity * p.product.discount_price
            amount += value
            total_quantity += p.quantity

        shipping_price = total_quantity * 10
        totalamount = amount + shipping_price
        data = {
            'amount': amount,
            'totalamount': totalamount
        }
        return JsonResponse(data)

