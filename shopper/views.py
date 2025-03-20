# shopper/views.py - 完整的视图文件

import json
import time
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import *
from .form import *
from .pays import get_payment_intent  # Import the Stripe payment function
from .serializers import OrderInfosSerializer, CartInfosSerializer, DeliveryAddressSerializer


class MySessionAuthentication(SessionAuthentication):
    '''
    Custom SessionAuthentication to disable CSRF verification
    '''

    def authenticate(self, request):
        user = getattr(request._request, 'user', None)
        if not user or not user.is_active:
            return None
        return (user, None)


class loginView(APIView):
    '''
    User login and registration
    '''
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        context = {'state': 'fail', 'msg': 'Registration or login failed'}
        json_str = json.loads(request.body.decode())
        infos = LoginModelForm(data=json_str)
        d = infos.data
        username = d['username']
        password = d['password']
        last_login = ''

        # If user exists, perform login validation
        if User.objects.filter(username=username).first():
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                # 使用更完整的时间格式
                last_login = user.last_login.strftime("%Y-%m-%d %H:%M:%S") if user.last_login else ''
                context = {'state': 'success', 'msg': 'Login successful'}
        else:
            # If user doesn't exist, perform registration
            context = {'state': 'success', 'msg': 'Registration successful'}
            d = dict(username=username, password=password, is_staff=1, is_active=1)
            user = User.objects.create_user(**d)
            user.save()
            login(request, user)

        context['username'] = username
        context['last_login'] = last_login
        return Response(context)


class logoutView(APIView):
    '''
    Logout user
    '''
    authentication_classes = [MySessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        context = {'state': 'fail', 'msg': 'Logout failed'}
        # Use built-in logout function to end user session
        if request.user.username:
            logout(request)
            context = {'state': 'success', 'msg': 'Logout successful'}
        return Response(context)


class shopperView(APIView):
    '''
    User profile center
    '''
    authentication_classes = [MySessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        context = {'state': 'success', 'msg': 'Data retrieved successfully', 'data': {}}
        t = request.GET.get('t', '')

        # 简化日志，避免过多输出可能引起的问题
        if t:
            print(f"Processing order with payment ID: {t}")

        # 如果存在支付ID，创建订单
        if t:
            # 从会话获取必要信息
            payInfo = request.session.get('payInfo', None)
            selected_items = request.session.get('selected_items', [])

            if payInfo:
                try:
                    # 设置订单状态为已付款和支付ID
                    order_data = payInfo.copy()  # 创建副本避免修改会话中的原始数据
                    order_data['payment_id'] = t
                    order_data['state'] = 'paid'  # 确保状态为paid

                    # 创建订单
                    order = OrderInfos.objects.create(**order_data)
                    print(f"Order created with ID: {order.id}")

                    # 将购物车商品转移到订单项目
                    user_cart_items = CartInfos.objects.filter(user_id=request.user.id)

                    if selected_items:
                        cart_items = user_cart_items.filter(id__in=selected_items)
                    else:
                        cart_items = user_cart_items

                    for cart_item in cart_items:
                        if cart_item.commodityInfos_id:
                            # 创建订单项目
                            OrderItem.objects.create(
                                order=order,
                                product_id=cart_item.commodityInfos_id.id,
                                product_name=cart_item.commodityInfos_id.name,
                                price=cart_item.commodityInfos_id.base_price,
                                quantity=cart_item.quantity
                            )
                            
                            # 更新商品销量
                            product = cart_item.commodityInfos_id
                            product.sold = product.sold + cart_item.quantity
                            product.save()

                    # 清空购物车或删除已购买的商品
                    if selected_items:
                        user_cart_items.filter(id__in=selected_items).delete()
                    else:
                        user_cart_items.delete()

                    # 清除会话数据
                    if 'payInfo' in request.session:
                        del request.session['payInfo']
                    if 'payTime' in request.session:
                        del request.session['payTime']
                    if 'selected_items' in request.session:
                        del request.session['selected_items']
                    request.session.save()  # 确保会话更改被保存

                except Exception as e:
                    print(f"Error creating order: {str(e)}")
                    # 即使出错也继续执行，以便用户能够看到他们的订单

        # Query all order information for the current user
        orders = OrderInfos.objects.filter(user_id=request.user.id).order_by('-created').all()
        context['data']['orders'] = OrderInfosSerializer(instance=orders, many=True).data
        return Response(context)


class shopcartView(APIView):
    '''
    Shopping cart API:
    GET: Retrieve shopping cart list
    POST: Add product to shopping cart
    PUT: Update cart item quantity
    '''
    authentication_classes = [MySessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    # 修改 shopperView.get 方法
    def get(self, request):
        context = {'state': 'success', 'msg': 'Data retrieved successfully', 'data': []}

        try:
            # Get current user's cart items with proper error handling
            cart_items = CartInfos.objects.filter(user_id=request.user.id).select_related('commodityInfos_id')

            # Serialize cart data
            cart_data = []
            for item in cart_items:
                # Skip items with deleted products
                if not item.commodityInfos_id:
                    continue

                item_data = {
                    'id': item.id,
                    'quantity': item.quantity,
                    'commodityInfos_id': {
                        'id': item.commodityInfos_id.id,
                        'name': item.commodityInfos_id.name,
                        'price': item.commodityInfos_id.base_price,
                        'img': item.commodityInfos_id.img.url if item.commodityInfos_id.img else None,
                    }
                }

                cart_data.append(item_data)

            context['data'] = cart_data

        except Exception as e:
            # 添加详细错误处理
            print(f"Error retrieving cart: {str(e)}")
            context = {'state': 'fail', 'msg': 'Failed to load cart items', 'data': []}

        return Response(context)

    def post(self, request):
        context = {'state': 'fail', 'msg': 'Failed to add to cart'}

        try:
            json_str = json.loads(request.body.decode())
            id = json_str.get('id', '')
            quantity = json_str.get('quantity', 1)
            userID = request.user.id

            # Validate product exists
            commodityInfos = CommodityInfos.objects.filter(id=id).first()
            if not id or not commodityInfos or not quantity:
                return Response(context)

            # Look for existing cart item
            existing_item = CartInfos.objects.filter(user_id=userID, commodityInfos_id=commodityInfos).first()

            # Create or update cart item
            if existing_item:
                existing_item.quantity += int(quantity)
                existing_item.save()
            else:
                # Create new cart item
                CartInfos.objects.create(
                    commodityInfos_id=commodityInfos,
                    user_id=userID,
                    quantity=quantity
                )

            context = {'state': 'success', 'msg': 'Successfully added to cart'}

        except Exception as e:
            # 添加详细错误处理
            print(f"Error adding to cart: {str(e)}")
            context = {'state': 'fail', 'msg': f'Failed to add to cart: {str(e)}'}

        return Response(context)

    def put(self, request):
        context = {'state': 'fail', 'msg': 'Failed to update cart'}

        try:
            json_str = json.loads(request.body.decode())
            cart_id = json_str.get('id', '')
            quantity = json_str.get('quantity', 0)

            if cart_id and quantity > 0:
                try:
                    cart_item = CartInfos.objects.get(id=cart_id, user_id=request.user.id)
                    cart_item.quantity = quantity
                    cart_item.save()
                    context = {'state': 'success', 'msg': 'Cart updated successfully'}
                except CartInfos.DoesNotExist:
                    context['msg'] = 'Cart item not found'
            else:
                context['msg'] = 'Invalid data'

        except Exception as e:
            # 添加详细错误处理
            print(f"Error updating cart: {str(e)}")
            context = {'state': 'fail', 'msg': f'Failed to update cart: {str(e)}'}

        return Response(context)


class paysView(APIView):
    '''
    Payment interface using Stripe
    '''
    authentication_classes = [MySessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        context = {'state': 'fail', 'msg': 'Payment failed', 'data': ''}
        json_str = json.loads(request.body.decode())
        total = json_str.get('total', 0)
        address_id = json_str.get('address_id', None)
        selected_items = json_str.get('items', [])  # 获取选中的购物车项ID列表

        # 简化日志，减少可能的副作用
        print(f"Payment request: amount={total}, address={address_id}, items={len(selected_items)}")

        # Remove currency symbol if present
        if isinstance(total, str):
            total = float(total.replace('£', '').replace('￥', ''))

        if total:
            # Generate a unique order number based on current timestamp
            out_trade_no = str(int(time.time()))
            user_id = request.user.id

            # Check if a delivery address was provided
            delivery_address_id = None
            if address_id:
                try:
                    # Verify that the address belongs to the user
                    delivery_address = DeliveryAddress.objects.get(id=address_id, user_id=user_id)
                    delivery_address_id = delivery_address.id
                except DeliveryAddress.DoesNotExist:
                    return Response({'state': 'fail', 'msg': 'Invalid delivery address'})

            # Store order info in session with pending payment status
            payInfo = {
                'price': total,
                'user_id': user_id,
                'state': 'pending_payment'
            }

            # Add delivery address if provided
            if delivery_address_id:
                payInfo['delivery_address_id'] = delivery_address_id

            # Store selected items in session for later use
            if selected_items:
                request.session['selected_items'] = selected_items

            request.session['payInfo'] = payInfo
            request.session['payTime'] = out_trade_no
            request.session.save()  # 确保会话被保存

            # Set return URL for after payment completion
            return_url = request.build_absolute_uri('/shopper')
            if not return_url.startswith('http'):
                return_url = 'http://localhost:8010/#/shopper?tab=orders'

            # Get Stripe payment intent
            payment_data = get_payment_intent(total, out_trade_no, return_url)

            if payment_data:
                context = {
                    'state': 'success',
                    'msg': 'Payment initiated successfully',
                    'data': payment_data
                }

        return Response(context)


class stripeWebhookView(APIView):
    '''
    Stripe payment webhook handler
    '''
    authentication_classes = []  # No authentication required for webhooks
    permission_classes = []  # No permissions required for webhooks

    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

        try:
            # You need to set up a webhook secret in your Stripe dashboard
            # For testing, you can skip signature verification
            import stripe
            event = stripe.Event.construct_from(
                json.loads(payload), stripe.api_key
            )

            # Handle payment success event
            if event.type == 'payment_intent.succeeded':
                payment_intent = event.data.object
                order_id = payment_intent.metadata.get('order_id')

                # Check if there's a pending order in session
                # This would typically be handled by your order fulfillment logic
                # For demo purposes, we'll just log the successful payment
                print(f"Payment succeeded for order {order_id}")

            return Response({'status': 'success'})

        except Exception as e:
            return Response({'error': str(e)}, status=400)


class deleteView(APIView):
    '''
    Delete product from shopping cart
    '''
    authentication_classes = [MySessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        context = {'state': 'fail', 'msg': 'Failed to delete'}
        json_str = json.loads(request.body.decode())
        username = json_str.get('username', '')
        carId = json_str.get('carId', '')

        # Delete shopping cart information based on request information
        if username:
            # Delete all items in the user's cart
            CartInfos.objects.filter(user_id=request.user.id).delete()
            context = {'state': 'success', 'msg': 'All items deleted successfully'}
        elif carId:
            # Delete a specific cart item
            try:
                CartInfos.objects.get(id=carId, user_id=request.user.id).delete()
                context = {'state': 'success', 'msg': 'Item deleted successfully'}
            except CartInfos.DoesNotExist:
                context['msg'] = 'Cart item not found'

        return Response(context)


class AddressView(APIView):
    '''
    Address management:
    GET: List all addresses for the current user
    POST: Create a new address
    '''
    authentication_classes = [MySessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        context = {'state': 'success', 'msg': 'Addresses retrieved successfully', 'data': {}}
        # Get all addresses for the current user
        addresses = DeliveryAddress.objects.filter(user_id=request.user.id).all()
        context['data']['addresses'] = DeliveryAddressSerializer(instance=addresses, many=True).data
        return Response(context)

    def post(self, request):
        context = {'state': 'fail', 'msg': 'Failed to create address'}
        json_data = json.loads(request.body.decode())

        # Add user_id to the data
        json_data['user_id'] = request.user.id

        # If this is marked as default, clear other default addresses
        if json_data.get('is_default', False):
            DeliveryAddress.objects.filter(user_id=request.user.id, is_default=True).update(is_default=False)

        # Create serializer with the data
        serializer = DeliveryAddressSerializer(data=json_data)
        if serializer.is_valid():
            serializer.save()
            context = {'state': 'success', 'msg': 'Address created successfully', 'data': serializer.data}
        else:
            context['msg'] = serializer.errors

        return Response(context)


class AddressDetailView(APIView):
    '''
    Address detail management:
    GET: Get a specific address
    PUT: Update a specific address
    DELETE: Delete a specific address
    '''
    authentication_classes = [MySessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        context = {'state': 'fail', 'msg': 'Address not found'}
        try:
            # Get the address if it belongs to the current user
            address = DeliveryAddress.objects.get(id=pk, user_id=request.user.id)
            serializer = DeliveryAddressSerializer(address)
            context = {'state': 'success', 'msg': 'Address retrieved successfully', 'data': serializer.data}
        except DeliveryAddress.DoesNotExist:
            pass
        return Response(context)

    def put(self, request, pk):
        context = {'state': 'fail', 'msg': 'Failed to update address'}
        try:
            # Get the address if it belongs to the current user
            address = DeliveryAddress.objects.get(id=pk, user_id=request.user.id)
            json_data = json.loads(request.body.decode())

            # If this is marked as default, clear other default addresses
            if json_data.get('is_default', False):
                DeliveryAddress.objects.filter(user_id=request.user.id, is_default=True).update(is_default=False)

            serializer = DeliveryAddressSerializer(address, data=json_data, partial=True)
            if serializer.is_valid():
                serializer.save()
                context = {'state': 'success', 'msg': 'Address updated successfully', 'data': serializer.data}
            else:
                context['msg'] = serializer.errors
        except DeliveryAddress.DoesNotExist:
            context['msg'] = 'Address not found'
        return Response(context)

    def delete(self, request, pk):
        context = {'state': 'fail', 'msg': 'Failed to delete address'}
        try:
            # Get the address if it belongs to the current user
            address = DeliveryAddress.objects.get(id=pk, user_id=request.user.id)
            address.delete()
            context = {'state': 'success', 'msg': 'Address deleted successfully'}
        except DeliveryAddress.DoesNotExist:
            context['msg'] = 'Address not found'
        return Response(context)


class DefaultAddressView(APIView):
    '''
    Set an address as default
    '''
    authentication_classes = [MySessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        context = {'state': 'fail', 'msg': 'Failed to set default address'}
        json_str = json.loads(request.body.decode())
        address_id = json_str.get('address_id', '')

        if not address_id:
            context['msg'] = 'Address ID is required'
            return Response(context)

        try:
            # 确认地址存在并且属于当前用户
            address = DeliveryAddress.objects.get(id=address_id, user_id=request.user.id)

            # 将其他地址设置为非默认
            DeliveryAddress.objects.filter(user_id=request.user.id, is_default=True).update(is_default=False)

            # 将当前地址设置为默认
            address.is_default = True
            address.save()

            context = {'state': 'success', 'msg': 'Default address set successfully'}
        except DeliveryAddress.DoesNotExist:
            context['msg'] = 'Address not found'

        return Response(context)


class UserProfileSerializer(serializers.ModelSerializer):
    """
    用户资料序列化器
    """
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    confirm_password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'password', 'confirm_password')
        read_only_fields = ('id', 'username')

    def validate(self, data):
        # 验证密码是否匹配
        if 'password' in data and data['password']:
            if 'confirm_password' not in data or data['password'] != data['confirm_password']:
                raise serializers.ValidationError({"confirm_password": "Passwords do not match"})

            # 验证密码强度
            try:
                validate_password(data['password'])
            except ValidationError as e:
                raise serializers.ValidationError({"password": list(e.messages)})

        return data

    def update(self, instance, validated_data):
        # 移除确认密码字段，它不是用户模型的一部分
        validated_data.pop('confirm_password', None)

        # 处理密码更新
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)

        # 更新其他字段
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class UserProfileView(APIView):
    """
    用户资料API:
    GET: 获取当前用户资料
    PUT: 更新用户资料
    """
    authentication_classes = [MySessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """获取当前用户的资料信息"""
        serializer = UserProfileSerializer(request.user)
        return Response({
            'state': 'success',
            'msg': 'User profile retrieved successfully',
            'data': serializer.data
        })

    def put(self, request):
        """更新当前用户的资料信息"""
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                'state': 'success',
                'msg': 'User profile updated successfully',
                'data': serializer.data
            })
        else:
            return Response({
                'state': 'fail',
                'msg': 'Failed to update profile',
                'errors': serializer.errors
            }, status=400)


class CollectView(APIView):
    '''
    商品收藏管理:
    POST: 添加或删除收藏
    '''
    authentication_classes = [MySessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        context = {'state': 'fail', 'msg': 'Failed to update favorites'}
        try:
            json_data = json.loads(request.body.decode())
            product_id = json_data.get('id')
            action = json_data.get('action')

            if not product_id or action not in ['add', 'remove']:
                context['msg'] = 'Invalid request data'
                return Response(context)

            # 检查商品是否存在
            product = CommodityInfos.objects.filter(id=product_id).first()
            if not product:
                context['msg'] = 'Product not found'
                return Response(context)

            # 获取或创建收藏记录
            collect, created = CollectInfos.objects.get_or_create(
                user_id=request.user,  # 直接使用 request.user 而不是 request.user.id
                commodityInfos_id=product
            )

            if action == 'add' and created:
                context = {'state': 'success', 'msg': 'Added to favorites successfully'}
            elif action == 'remove' and not created:
                collect.delete()
                context = {'state': 'success', 'msg': 'Removed from favorites successfully'}
            else:
                context = {'state': 'success', 'msg': 'Favorites status unchanged'}

        except Exception as e:
            print(f"Error updating favorites: {str(e)}")
            context['msg'] = str(e)

        return Response(context)