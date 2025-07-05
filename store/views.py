from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category, Cart, CartItem, Order, OrderItem, Review
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.db.models import Q, Avg, Count
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import UserProfileForm, ReviewForm
from django.contrib import messages
from django.conf import settings
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _cart_id(request)
        )
        cart.save()
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product = product,
            quantity = 1,
            cart = cart
        )
        cart_item.save()
    messages.success(request, f'{product.name} has been added to your cart.')
    return redirect('cart_detail')

def cart_detail(request, total=0, counter=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            counter += cart_item.quantity
    except Cart.DoesNotExist:
        pass
    return render(request, 'store/cart.html', dict(cart_items = cart_items, total = total, counter = counter))

def remove_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart.objects.get(cart_id=_cart_id(request))
    cart_item = CartItem.objects.get(product=product, cart=cart)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    messages.success(request, f'{product.name} has been removed from your cart.')
    return redirect('cart_detail')

def remove_full_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart.objects.get(cart_id=_cart_id(request))
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    messages.success(request, f'{product.name} has been removed from your cart.')
    return redirect('cart_detail')

@login_required
def checkout(request):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    cart_items = CartItem.objects.filter(cart=cart, active=True)
    total = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        
        order = Order.objects.create(user=request.user, total=total, payment_method=payment_method)
        order.save()

        if payment_method == 'Cash on Delivery':
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
                cart_item.delete() # Clear cart item after creating order item

            messages.success(request, 'Your order has been placed successfully!')
            return redirect('order_confirmation', order_id=order.id)
        elif payment_method == 'Stripe':
            line_items = []
            for item in cart_items:
                line_items.append({
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': item.product.name,
                        },
                        'unit_amount': int(item.product.price * 100), # Stripe expects amount in cents
                    },
                    'quantity': item.quantity,
                })
            try:
                checkout_session = stripe.checkout.Session.create(
                    line_items=line_items,
                    mode='payment',
                    success_url=request.build_absolute_uri(f'/order_confirmation/?session_id={{CHECKOUT_SESSION_ID}}'),
                    cancel_url=request.build_absolute_uri('/checkout/'),
                    metadata={
                        'user_id': request.user.id,
                        'cart_id': cart.id,
                        'order_id': order.id, # Pass the order ID to Stripe metadata
                    }
                )
                return redirect(checkout_session.url, code=303)
            except Exception as e:
                messages.error(request, f'Error processing Stripe payment: {e}')
                order.delete() # Delete the order if Stripe checkout fails
                return redirect('checkout')
    
    return render(request, 'store/checkout.html', {'total': total, 'cart_items': cart_items, 'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY})

@login_required
def order_confirmation(request, order_id=None):
    order = None
    order_items = None
    if order_id:
        order = get_object_or_404(Order, id=order_id, user=request.user)
        order_items = OrderItem.objects.filter(order=order)
    elif 'session_id' in request.GET:
        session_id = request.GET.get('session_id')
        try:
            checkout_session = stripe.checkout.Session.retrieve(session_id)
            # Assuming you stored order_id in metadata
            order_id_from_metadata = checkout_session.metadata.get('order_id')
            if order_id_from_metadata:
                order = get_object_or_404(Order, id=order_id_from_metadata, user=request.user)
                order_items = OrderItem.objects.filter(order=order)
            else:
                messages.error(request, "Order ID not found in Stripe session metadata.")
                return redirect('product_list')
        except stripe.error.StripeError as e:
            messages.error(request, f"Error retrieving Stripe session: {e}")
            return redirect('product_list')
    else:
        messages.error(request, "No order information provided.")
        return redirect('product_list')

    return render(request, 'store/order_confirmation.html', {'order': order, 'order_items': order_items})

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # Fulfill the purchase...
        # You can retrieve the order based on the metadata you passed during session creation
        user_id = session.metadata.get('user_id')
        cart_id = session.metadata.get('cart_id')
        order_id = session.metadata.get('order_id') # If you passed order_id

        if order_id:
            try:
                order = Order.objects.get(id=order_id)
                order.status = 'Processing' # Or 'Paid' or similar
                order.payment_method = 'Stripe'
                order.save()
                # Clear the cart if necessary
                # Cart.objects.filter(id=cart_id).delete()
            except Order.DoesNotExist:
                print(f"Order with ID {order_id} not found.")
        else:
            print("Order ID not found in webhook metadata.")

    return HttpResponse(status=200)

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at').prefetch_related('orderitem_set__product')
    return render(request, 'store/order_history.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)
    return render(request, 'store/order_detail.html', {'order': order, 'order_items': order_items})

@login_required
def profile(request):
    return render(request, 'store/profile.html')

@login_required
def profile_edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, instance=request.user.userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
        else:
            for field, errors in user_form.errors.items():
                for error in errors:
                    messages.error(request, f"User - {field}: {error}")
            for field, errors in profile_form.errors.items():
                for error in errors:
                    messages.error(request, f"Profile - {field}: {error}")
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.userprofile)
    return render(request, 'store/profile_edit.html', {'user_form': user_form, 'profile_form': profile_form})

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products_list = Product.objects.all().annotate(average_rating=Avg('reviews__rating'), review_count=Count('reviews'))

    sort_by = request.GET.get('sort_by', 'name') # Default sort by name

    if sort_by == 'price_asc':
        products_list = products_list.order_by('price')
    elif sort_by == 'price_desc':
        products_list = products_list.order_by('-price')
    elif sort_by == 'date_asc':
        products_list = products_list.order_by('created_at')
    elif sort_by == 'date_desc':
        products_list = products_list.order_by('-created_at')
    elif sort_by == 'rating_desc':
        products_list = products_list.order_by('-average_rating')
    else:
        products_list = products_list.order_by('name')
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products_list = products_list.filter(category=category)

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if min_price:
        products_list = products_list.filter(price__gte=min_price)
    if max_price:
        products_list = products_list.filter(price__lte=max_price)

    paginator = Paginator(products_list, 6) # Show 6 products per page
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, 'store/product_list.html', {
        'category': category,
        'categories': categories,
        'products': products
    })

def product_detail(request, slug):
    product = get_object_or_404(Product.objects.annotate(average_rating=Avg('reviews__rating'), review_count=Count('reviews')), slug=slug)
    reviews = Review.objects.filter(product=product)

    # Recently Viewed Products Logic
    recently_viewed_products_ids = request.session.get('recently_viewed', [])

    # Add current product to the list, ensuring it's at the beginning and unique
    if product.id in recently_viewed_products_ids:
        recently_viewed_products_ids.remove(product.id)
    recently_viewed_products_ids.insert(0, product.id)

    # Limit the list to a certain number (e.g., 5)
    recently_viewed_products_ids = recently_viewed_products_ids[:5]
    request.session['recently_viewed'] = recently_viewed_products_ids

    # Fetch the actual product objects for recently viewed products
    recently_viewed_products = Product.objects.filter(id__in=recently_viewed_products_ids).exclude(id=product.id)
    # Order them by the order in the list
    recently_viewed_products = sorted(recently_viewed_products, key=lambda p: recently_viewed_products_ids.index(p.id))

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, 'Your review has been submitted successfully!')
            return redirect('product_detail', slug=slug)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = ReviewForm()
    return render(request, 'store/product_detail.html', {'product': product, 'reviews': reviews, 'form': form, 'recently_viewed_products': recently_viewed_products})

from django.contrib.auth.forms import UserCreationForm
from .forms import UserProfileForm, ReviewForm, CustomUserCreationForm

# ... (rest of the existing code above this point)

def register(request):
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.first_name = user_form.cleaned_data.get('first_name')
            user.last_name = user_form.cleaned_data.get('last_name')
            user.email = user_form.cleaned_data.get('email')
            user.save()
            # Save UserProfile after User is saved
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            login(request, user)
            messages.success(request, 'Registration successful. You are now logged in.')
            return redirect('product_list')
        else:
            for field, errors in user_form.errors.items():
                for error in errors:
                    messages.error(request, f"User - {field}: {error}")
            for field, errors in profile_form.errors.items():
                for error in errors:
                    messages.error(request, f"Profile - {field}: {error}")
    else:
        user_form = CustomUserCreationForm()
        profile_form = UserProfileForm()
    return render(request, 'registration/register.html', {'user_form': user_form, 'profile_form': profile_form})

from .models import Product, Category, Cart, CartItem, Order, OrderItem, Review, Wishlist

# ... (rest of the existing code above this point)

def search(request):
    products_list = Product.objects.all().order_by('name')
    query = None

    if 'q' in request.GET:
        query = request.GET.get('q')
        products_list = products_list.filter(Q(name__contains=query) | Q(description__contains=query))

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if min_price:
        products_list = products_list.filter(price__gte=min_price)
    if max_price:
        products_list = products_list.filter(price__lte=max_price)

    paginator = Paginator(products_list, 6) # Show 6 products per page
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, 'store/product_list.html', {'query': query, 'products': products, 'categories': Category.objects.all()})

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if created:
        messages.success(request, f'{product.name} has been added to your wishlist.')
    else:
        messages.info(request, f'{product.name} is already in your wishlist.')
    return redirect('product_detail', slug=product.slug)

@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        wishlist_item = Wishlist.objects.get(user=request.user, product=product)
        wishlist_item.delete()
        messages.success(request, f'{product.name} has been removed from your wishlist.')
    except Wishlist.DoesNotExist:
        messages.error(request, f'{product.name} was not found in your wishlist.')
    return redirect('wishlist_view')

@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/wishlist.html', {'wishlist_items': wishlist_items})
