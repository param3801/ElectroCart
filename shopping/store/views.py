from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib import messages
from django.views import View
from .models.product import Product 
from .models.category import Category
from .models.customer import Customer
from .models.cart import Cart
from .models.order import OrderDetail

from django.db.models import Q
from django.http import JsonResponse
 



def home(request): 
    products = None
    total_item=0
    if request.session.has_key('phone'):
        phone=request.session['phone']
        total_item=len(Cart.objects.filter(phone=phone))

        category = Category.get_all_categories()
        customer = Customer.objects.filter(phone=phone)
        for c in customer:
            name = c.username

            categoryID = request.GET.get('category')
            if categoryID:
                products = Product.get_all_product_by_category_id(categoryID)
                data = {}  
                data['name']=name
                data['product'] = products
                # data['category'] = category
                data['total_item']=total_item
                return render(request,'home.html',data) 


            else:
                products = Product.get_all_products()       

                data = {}  
                data['name']=name
                data['product'] = products
                data['category'] = category
                data['total_item']=total_item
                # print(request.session.get('phone'))
                return render(request,'home.html',data) 
    
    
    else:
        return redirect('login') 




class Register(View):
    def get(self,request):
        return render(request,'register.html')
    def post(self,request):
        postData = request.POST
        username = postData.get('username')
        phone = postData.get('mobile')
        email = postData.get('email')

        error_message = None
        value = {
             'username': username,
             'phone':phone,
             'email':email
        }

        customer = Customer(username=username,
                            phone=phone)
        
        if(not username):
            error_message = "Username is required!"

        elif(not phone):
            error_message = "phone is required!"  

        elif(len(phone)<10):
            error_message = "phone number must be 10 character long or more!"

        elif customer.isexist():
            error_message="phone number already registered!"    

        if not error_message:
            messages.success(request,'Conguration register successfully!', extra_tags='alert')         

            customer.registers()
            return redirect('register') 
        
        else:
            data = {
                'error':error_message,
                'value':value
            }
            return render(request,'register.html',data)
        

class Login(View):
    def get(self,request):
        return render(request,'login.html')
    def post(self,request):
        phone = request.POST.get('phone')

        error_message = None
        value = {
            'phone':phone
        }
        customer = Customer.objects.filter(phone = request.POST["phone"])
        if customer:
            request.session['phone'] = phone
            return redirect('homepage')
        else:
            error_message = "phone number is invalid!"
            data = {
                'value':value,
                'error':error_message,
            }
            return render(request ,'login.html', data) 
        

def productdetail(request,pk):
    total_item=0
    product = Product.objects.get(pk = pk)
    item_already_in_cart=False
    if request.session.has_key('phone'):
        phone=request.session['phone']
        total_item=len(Cart.objects.filter(phone=phone))
        item_already_in_cart=Cart.objects.filter(Q(product=product.id)& Q(phone=phone)).exists()
        customer = Customer.objects.filter(phone=phone)
        for c in customer:
            name=c.username
        data={
            'product':product,
            'item_already_in_cart':item_already_in_cart,
            'name':name,
            'total_item':total_item
        }

     
        return render(request,'productdetail.html',data)     



def logut(request):
    if request.session.has_key('phone'):
        del request.session['phone']
        return redirect('login')
    else:
        return redirect('login')



def add_to_cart(request):
    phone=request.session['phone']
    product_id = request.GET.get('prod_id')
    product_name = Product.objects.get(id=product_id)
    product = Product.objects.filter(id=product_id)
    for p in product:
        image = p.image
        price=p.price
        Cart(phone=phone,product=product_name,image=image,price=price).save()
        return redirect(f'/product-detail/{product_id}')
      




def show_cart(request):
    total_item=0
    if request.session.has_key('phone'):
        phone=request.session['phone']
        total_item=len(Cart.objects.filter(phone=phone))
        customer = Customer.objects.filter(phone=phone)
        for c in customer:
            name=c.username
            cart = Cart.objects.filter(phone=phone)
            data ={
                'name':name,
                "total_item":total_item,
                'cart':cart
            }
            if cart:
                return render(request,'show_cart.html',data)
            else:
                return render(request,'empty_cart.html',data)
    else:
        return redirect('login')
                

def plus_cart(request):
    if request.session.has_key('phone'):
        phone=request.session['phone']
        product_id = request.GET['prod_id']
        cart = Cart.objects.get(Q(product=product_id) & Q(phone=phone))
        cart.quantity+=1
        
        cart.save()

        data={
            'quantity': cart.quantity
        }
        return JsonResponse(data)



def minus_cart(request):

    if request.session.has_key('phone'):
        phone=request.session['phone']
        product_id = request.GET['prod_id']
        cart = Cart.objects.get(Q(product=product_id) & Q(phone=phone))
        cart.quantity-=1
        
        cart.save()

        data={
            'quantity': cart.quantity
        }
        return JsonResponse(data)
    

def remove_cart(request):

    if request.session.has_key('phone'):
        phone=request.session['phone']
        product_id = request.GET['prod_id']
        cart = Cart.objects.get(Q(product=product_id) & Q(phone=phone))
        cart.delete()
        return redirect('show_cart')  

def checkout(request):
    total_item=0
    if request.session.has_key('phone'):
        phone=request.session['phone']
        name= request.POST.get('name')
        address= request.POST.get('address')
        mobile= request.POST.get('mobile')
        # print(name,address,mobile)
        cart_product=Cart.objects.filter(phone=phone)
        for c in cart_product:
            qty=c.quantity
            price = c.price
            product_name=c.product
            image= c.image
 
            OrderDetail(user=phone,product_name=product_name,image=image,qty=qty,price=price).save()
            cart_product.delete() 
            total_item=len(Cart.objects.filter(phone=phone))
            customer = Customer.objects.filter(phone=phone)
            for c in customer:
                name=c.username
            data ={
                'name':name,
                "total_item":total_item
            }  
            return render(request,'empty_cart.html',data)
        
    else:
        return redirect('login')
        

def order(request):
    total_item=0
    if request.session.has_key('phone'):
        phone=request.session['phone']

        total_item=len(Cart.objects.filter(phone=phone))
        customer = Customer.objects.filter(phone=phone)
        for c in customer:
            name=c.username
        order= OrderDetail.objects.filter(user=phone)

        data={
            'order':order,
            'name':name,
            'total_item':total_item
        }
        if order:

            return render(request,'order.html',data)        

        else:
            return render(request,'empty_order.html',data)        

    else:
        return redirect('login')
        


def search(request):
    total_item=0
    if request.session.has_key('phone'):
        phone=request.session['phone']
        query = request.GET.get('query')
        search= Product.objects.filter(name__contains=query)
        category = Category.get_all_categories()


        total_item=len(Cart.objects.filter(phone=phone))
        customer = Customer.objects.filter(phone=phone)
        for c in customer:
            name=c.username 
        data ={
            'name':name,
            'total_item':total_item,
            'search': search,
            'category':category,
            'query':category


        }
        return render(request,'search.html',data)
    else:
        return redirect('login')





