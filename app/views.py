from django.shortcuts import render,redirect
from django.views import View
from .models import *
from .forms import *
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class HomeView(View):
    def get(self, request):
        topwears = Product.objects.filter(category='TW')
        bottomwears = Product.objects.filter(category='BW')
        mobiles = Product.objects.filter(category='M')
        laptops = Product.objects.filter(category='L')
        return render(request, 'app/home.html', {'topwears': topwears,
                                                 'bottomwears': bottomwears,
                                                 'mobiles': mobiles,
                                                 'laptops':laptops})


# def home(request):
#  return render(request, 'app/home.html')

class ProductDetailView(View):
    def get(self,request,pk):
        product = Product.objects.get(pk=pk)
        item_already_in_cart = False
        if request.user.is_authenticated:
            item_already_in_cart = Cart.objects.filter(Q(product=product.id) &
                                                       Q(user=request.user)).exists()
        return render(request,'app/productdetail.html',{'product':product,
                                                        'item_already_in_cart':item_already_in_cart})




# def product_detail(request):
#     return render(request, 'app/productdetail.html')

@login_required()
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    Cart(user=user,product=product).save()
    return redirect('show-cart')


def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity+=1
        c.save()
        amount = 0.0
        shipping_amount = 70
        total_amount = 0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            temp_amount = (p.quantity * p.product.discount_price)
            amount += temp_amount
            total_amount = amount + shipping_amount

        data = {
            'quantity': c.quantity,
            'amount': amount,
            'total_amount': total_amount
        }
    return JsonResponse(data)

def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity-=1
        c.save()
        amount = 0.0
        shipping_amount = 70
        total_amount = 0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            temp_amount = (p.quantity * p.product.discount_price)
            amount += temp_amount
            total_amount = amount + shipping_amount

        data = {
            'quantity': c.quantity,
            'amount': amount,
            'total_amount': total_amount
        }
    return JsonResponse(data)


def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))

        c.delete()
        amount = 0.0
        shipping_amount = 70
        total_amount = 0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            temp_amount = (p.quantity * p.product.discount_price)
            amount += temp_amount
            total_amount = amount + shipping_amount

        data = {
            'amount': amount,
            'total_amount': total_amount
        }
    return JsonResponse(data)


@login_required()
def show_cart(request):
    if request.user.is_authenticated:
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0.0
        shipping_amount = 70
        total_amount = 0
        cart_product = [p for p in Cart.objects.all() if p.user == user]
        print(cart_product)
        if cart_product:
            for p in cart_product:
                temp_amount = (p.quantity * p.product.discount_price)
                amount += temp_amount
                total_amount = amount + shipping_amount
            return render(request, 'app/addtocart.html',{'carts':cart,
                                                     'total_amount':total_amount,
                                                     'amount':amount})
        else:
            return render(request,'app/emptycart.html')




def buy_now(request):
    return render(request, 'app/buynow.html')


# def profile(request):
#     return render(request, 'app/profile.html')

@method_decorator(login_required,name='dispatch')
class ProfileView(View):
    def get(self,request):
        form = CustomerProfileForm()
        return render(request, 'app/profile.html',{'form':form,'active':'btn-primary'})

    def post(self,request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            usr = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']

            reg = Customer(user=usr,
                           name=name,
                           locality=locality,
                           city=city,
                           state=state,
                           zipcode=zipcode)
            reg.save()

            messages.success(request,'Congratulations!! Profile Updated Successfully')
        return render(request,'app/profile.html',{'form':form,'active':'btn-primary'})





@login_required()
def address(request):
    add = Customer.objects.filter(user=request.user)
    return render(request, 'app/address.html',{'address':add,'active':'btn-primary'})




@login_required()
def orders(request):

    order = OrderPlaced.objects.filter(user=request.user)

    return render(request, 'app/orders.html',{'orders':order})


# def change_password(request):
#     return render(request, 'app/changepassword.html')


def mobile(request,data=None):
    if data == None:
        mobiles = Product.objects.filter(category='M')
    elif (data == 'Realme' or data == 'Samsung' or data == 'Nokia'):
        mobiles = Product.objects.filter(category='M').filter(brand=data)

    elif (data == 'below'):
        mobiles = Product.objects.filter(category='M').filter(discount_price__lt=8000)

    elif (data == 'above'):
        mobiles = Product.objects.filter(category='M').filter(discount_price__gt=8000)

    return render(request, 'app/mobile.html',{'mobiles':mobiles})

def laptop(request,data=None):
    if data == None:
        laptops = Product.objects.filter(category='L')
    elif (data == 'HP' or data == 'Dell'):
        laptops = Product.objects.filter(category='L').filter(brand=data)

    elif (data == 'below'):
        laptops = Product.objects.filter(category='L').filter(discount_price__lt=50000)

    elif (data == 'above'):
        laptops = Product.objects.filter(category='L').filter(discount_price__gt=50000)

    return render(request, 'app/laptop.html',{'laptops':laptops})


def topwear(request,data=None):
    if data == None:
        topwears = Product.objects.filter(category='TW')
    elif (data == 'Lee' or data == 'Roadstar' or data == 'Armani'):
        topwears = Product.objects.filter(category='TW').filter(brand=data)
    elif (data == 'below'):
        topwears = Product.objects.filter(category='TW').filter(discount_price__lt=400)

    elif (data == 'above'):
        topwears = Product.objects.filter(category='TW').filter(discount_price__gt=400)
        
    return render(request,'app/topwear.html',{'topwears':topwears})



def bottomwear(request,data=None):
    if data == None:
        bottomwears = Product.objects.filter(category='BW')
    elif (data == 'Lee' or data == 'Roadstar' or data == 'Armani' or data == 'spyke'):
        bottomwears = Product.objects.filter(category='BW').filter(brand=data)
    elif (data == 'below'):
        bottomwears = Product.objects.filter(category='BW').filter(discount_price__lt=400)

    elif (data == 'above'):
        bottomwears = Product.objects.filter(category='BW').filter(discount_price__gt=400)

    return render(request, 'app/bottomwear.html', {'bottomwears': bottomwears})




# def login(request):
#     return render(request, 'app/login.html')


class CustomerRegistrationView(View):
    def get(self,request):
        form = CustomerRegistraionForm()

        return render(request, 'app/customerregistration.html',{'form':form})


    def post(self,request):
        form = CustomerRegistraionForm(request.POST)
        if form.is_valid():
            messages.success(request,'Congratulations!! Registered Successfully')
            form.save()
        return render(request, 'app/customerregistration.html', {'form': form})







# def customerregistration(request):
#     return render(request, 'app/customerregistration.html')

@login_required()
def checkout(request):
    user = request.user
    address = Customer.objects.filter(user=user)
    cart_items = Cart.objects.filter(user=user)
    amount = 0.0
    shipping_amount = 70
    total_amount = 0
    cart_product = [p for p in Cart.objects.all() if p.user == user]
    print(cart_product)
    if cart_product:
        for p in cart_product:
            temp_amount = (p.quantity * p.product.discount_price)
            amount += temp_amount
            total_amount = amount + shipping_amount

    return render(request, 'app/checkout.html',{'address':address,'total_amount':total_amount,
                                                'cart_items':cart_items,'amount':amount})

def payment_done(request):
    user = request.user
    cust_id = request.GET.get('custid')

    customer = Customer.objects.get(id=cust_id)
    print(customer)
    cart = Cart.objects.filter(user=user)
    for c in cart:
        OrderPlaced(user=user,
                    customer=customer,
                    product=c.product,
                    quantity=c.quantity).save()

        c.delete()
    return redirect('orders')