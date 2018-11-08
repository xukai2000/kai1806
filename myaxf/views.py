from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import QueryDict

from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from myaxf.tasks import *
from .my_utils import *

from django.urls import reverse
from django.views.generic import View

from myaxf.models import *


def home(req):
    # 读取轮播数据
    wheels = Wheel.objects.all()
    nav = Nav.objects.all()
    musts = MustBuy.objects.all()
    shops = Shop.objects.all()

    data = {
        "title": "首页",
        "wheels": wheels,
        "navs": nav,
        "musts": musts,
        "shop0": shops[0],
        "shop1_3": shops[1:3],
        "shop3_7": shops[3:7],
        "shop_last": shops[7:],
        "mains": MainShow.objects.all()

    }
    return render(req, 'home/home.html', data)


def market(req):
    return redirect(reverse("axf:market_with_params", args=(104749, 0, 1)))


def market_with_params(req, typeid, sub_type_id, sort_type):
    """
        1 综合排序
        2 销量
        3 价格
    :param req:
    :param typeid:
    :param sub_type_id:
    :return:
    """
    # 拿到所有分数据
    my_types = GoodsTypes.objects.all()
    # 通过typeid拿商品数据
    my_goods = Goods.objects.filter(
        categoryid=typeid
    )
    # 拿一级分类数据
    current_type = my_types.filter(typeid=typeid).first()
    result = [i.split(":") for i in current_type.childtypenames.split("#")]
    # 通过二级分类过滤商品
    if sub_type_id == "0":
        result_goods = my_goods
    else:
        result_goods = my_goods.filter(childcid=sub_type_id)

    if sort_type == "2":
        result_goods = result_goods.order_by("productnum")
    # 排序
    if sort_type == "3":
        result_goods = result_goods.order_by("price")
    else:
        pass
    # 添加 num属性
    # 知道这个人的购物车属性
    user = req.user
    if isinstance(user, MyUser):
        # 设置字典接收数据方便查询数据
        tem_dict = {}
        # 去购物车查数据
        cart_nums = Cart.objects.filter(user=user)
        for i in cart_nums:
            tem_dict[i.goods.id] = i.num
        for i in result_goods:
            i.num = tem_dict.get(i.id) if tem_dict.get(i.id) else 0
    data = {
        "types": my_types,
        "goods": result_goods,
        "select_type_id": typeid,
        "sub_types": result,
        "select_sub_type_id": sub_type_id,

    }
    return render(req, 'market/market.html', data)


# 购物车，没登录跳到登录页面
@login_required(login_url="/axf/login")
def cart(req):
    # 确定用户
    user = req.user
    # 根据用户 去购物车数据搜索该用户数据
    data = Cart.objects.filter(user_id=user.id)
    # 算钱
    sum_money = get_cart_money(data)
    # 判断全选按钮状态(有购物车商品，并且有未被选购的产品)
    if data.exists() and not data.filter(is_selected=False).exists():
        is_all_select = True
    else:
        is_all_select = False
    result = {
        "title": "购物车",
        "uname": user.username,
        "phone": user.phone if user.phone else "暂无",
        "address": user.address if user.address else "暂无",
        "cart_items": data,
        "sum_money": sum_money,
        "is_all_select": is_all_select
    }
    return render(req, "cart/cart.html", result)


def mine(req):
    user = req.user
    is_login = False

    if isinstance(user, MyUser):
        is_login = True
    u_name = user.username if is_login else ""
    icon = "http://" + req.get_host() + "/static/uploads/" + user.icon.url if is_login else ""
    data = {
        "title": "我的",
        "u_name": u_name,
        "icon": icon,
        "is_login": is_login
    }

    return render(req, 'mine/mine.html', data)


class RegisterAPI(View):
    def get(self, req):
        return render(req, "user/register.html")

    def post(self, req):
        params = req.POST
        icon = req.FILES.get("u_icon")
        name = params.get("u_name")
        pwd = params.get("u_pwd")
        confirm_pwd = params.get("u_confirm_pwd")
        email = params.get("email")
        print(name, pwd)
        if pwd and confirm_pwd and pwd == confirm_pwd:
            if MyUser.objects.filter(username=name).exists():
                return render(req, "user/register.html", {"help_msg": "该用户已存在"})
            else:
                user = MyUser.objects.create_user(
                    username=name,
                    password=pwd,
                    email=email,
                    is_active=False,
                    icon=icon
                )
                # 生成验证链接
                url = "http://" + req.get_host() + "/axf/confirm/" + get_uuique_str()
                # 发邮件 异步调用
                send_verify_mail.delay(url, user.id, email)

                return redirect(reverse("axf:login"))


class LoginAPI(View):
    def get(self, req):
        return render(req, 'user/login.html')

    def post(self, req):
        # 解析参数
        params = req.POST
        name = params.get("name")
        pwd = params.get("pwd")
        # 校验数据
        print(name)
        print(pwd)
        if not name or not pwd:
            data = {
                "code": 2,
                "msg": "账号或密码不能为空",
                "data": ""
            }
            return JsonResponse(data)
        # 使用用户名，密码校验用户
        user = authenticate(username=name, password=pwd)
        if user:
            login(req, user)
            data = {
                "code": 1,
                "msg": "ok",
                "data": "/axf/mine"
            }
            return JsonResponse(data)

        else:
            data = {
                "code": 3,
                "msg": "账号或密码错误",
                "data": ""
            }
            return JsonResponse(data)


class LogoutAPI(View):
    def get(self, req):
        logout(req)
        return redirect(reverse("axf:mine"))


def confirm(req, uuid_str):
    # 去缓存拿数据
    #     若果拿到用户id 修改is_active
    print(uuid_str)
    user_id = cache.get(uuid_str)
    print(user_id)
    if user_id:
        user = MyUser.objects.get(pk=int(user_id))
        user.is_active = True
        user.save()
        return redirect(reverse("axf:login"))
    else:
        return HttpResponse("<h2>链接失效</h2>")


def check_uname(req):
    uname = req.GET.get("uname")

    print(uname)
    # 判段数据不能是空白，然后去搜 所数据
    data = {
        "code": 1,
        "data": ""
    }
    if uname and len(uname) >= 3:
        if MyUser.objects.filter(username=uname).exists():
            data["msg"] = "账号已存在"
        else:
            data["msg"] = "账号可用"
    else:
        data["msg"] = "用户名过短"
    return JsonResponse(data)


# 闪购添加页面，向购物车Cart中添加数据
class CartAPI(View):
    def post(self, req):
        user = req.user
        if not isinstance(user, MyUser):
            data = {
                "code": 2,
                "msg": "not login",
                "data": "/axf/login"
            }
            return JsonResponse(data)
        op_type = req.POST.get("type")
        g_id = int(req.POST.get("g_id"))
        goods = Goods.objects.get(pk=g_id)
        if op_type == "add":
            # 添加购物车操作
            goods_num = 1
            if goods.storenums > 1:
                cart_goods = Cart.objects.filter(
                    user=user,
                    goods=goods
                )
                if cart_goods.exists():
                    # 不是第一次添加
                    cart_item = cart_goods.first()
                    # 在原来基础上加1
                    cart_item.num = cart_item.num + 1
                    cart_item.save()
                    # 修改返回数量
                    goods_num = cart_item.num
                else:
                    # 第一次添加
                    Cart.objects.create(
                        user=user,
                        goods=goods
                    )
                data = {
                    "code": 1,
                    "msg": "ok",
                    "data": goods_num
                }
                return JsonResponse(data)
            else:
                data = {
                    "code": 3,
                    "msg": "库存不够",
                    "data": ""
                }
                return JsonResponse(data)
        elif op_type == "sub":
            goods_num = 0
            cart_item = Cart.objects.get(
                user=user,
                goods=goods
            )
            cart_item.num -= 1
            cart_item.save()
            if cart_item.num == 0:
                cart_item.delete()
            else:
                goods_num = cart_item.num
            data = {
                "code": 1,
                "msg": "ok",
                "data": goods_num
            }
            return JsonResponse(data)


# 购物车单个按钮的勾选
class CartStatuAPI(View):
    def patch(self, req):
        params = QueryDict(req.body)
        c_id = int(params.get("c_id"))
        user = req.user
        # 先拿到跟这个人有关系的购物车数据
        cart_items = Cart.objects.filter(user_id=user.id)
        # 拿到c_id对应的数据
        cart_data = cart_items.get(id=c_id)
        # 修改状态 取反
        cart_data.is_selected = not cart_data.is_selected
        cart_data.save()
        # 算钱
        sum_money = get_cart_money(cart_items)
        # 判断是否全选
        if cart_items.filter(is_selected=False).exists():
            is_all_select = False
        else:
            is_all_select = True
        # 返回数据
        result = {
            "code": 1,
            "msg": "ok",
            "data": {
                "is_select_all": is_all_select,
                "sum_money": sum_money,
                "status": cart_data.is_selected
            }
        }
        return JsonResponse(result)


# 购物车全选按钮
class CartAllStatusAPI(View):
    def put(self, req):
        user = req.user
        # 判断操作
        cart_items = Cart.objects.filter(user_id=user.id)
        is_select_all = False
        if cart_items.exists() and cart_items.filter(is_selected=False).exists():
            is_select_all = True
            # 由于当前处于未全选的状态，那么我们需要的操作
            # for i in cart_items.filter(is_selected=False):
            #     i.is_selected=True
            #     i.save()
            cart_items.filter(is_selected=False).update(is_selected=True)
            # 算钱
            sum_money = get_cart_money(cart_items)
        else:
            cart_items.update(is_selected=False)
            # 由于全不选,钱就是0
            sum_money = 0

        result = {
            "code": 1,
            "msg": "ok",
            "data": {
                "sum_money": sum_money,
                "all_select": is_select_all}
        }
        return JsonResponse(result)


class CartItemAPI(View):
    def post(self, req):
        # 用户
        user = req.user
        c_id = req.POST.get("c_id")
        # 确定购物车数据
        cart_item = Cart.objects.get(id=int(c_id))
        print(cart_item)
        if cart_item.goods.storenums < 1:
            data = {
                "code": 2,
                "msg": "库存不足",
                "data": ""
            }
            return JsonResponse(data)
        cart_item.num += 1
        cart_item.save()
        # 算钱
        cart_items = Cart.objects.filter(
            user_id=user.id,
            is_selected=True
        )
        sum_money = get_cart_money(cart_items)
        # 返回数据
        data = {
            "code": 1,
            "msg": "ok",
            "data": {
                "sum_money": sum_money,
                "num": cart_item.num
            }
        }
        return JsonResponse(data)

    def delete(self, req):
        user = req.user
        # 购物车商品
        c_id = QueryDict(req.body).get("c_id")
        cart_item = Cart.objects.get(pk=int(c_id))

        # 减数量
        cart_item.num -= 1
        cart_item.save()
        # 判断是否见到0
        if cart_item.num == 0:
            goods_num =0
            cart_item.delete()
        else:
            goods_num = cart_item.num
        # 算钱
        cart_items = Cart.objects.filter(
            user=user,
            is_selected=True
        )
        sum_money = get_cart_money(cart_items)

        data = {
            "code": 1,
            "msg": "ok",
            "data": {
                "num": goods_num,
                "sum_money": sum_money
            }

        }

        return JsonResponse(data)


class OrderAPI(View):
    def get(self, req):
        user = req.user
        cart_items = Cart.objects.filter(
            user_id=user.id,
            is_selected=True
        )

        order = Order.objects.create(
            user=user
        )
        for i in cart_items:
            OrderItem.objects.create(
                order=order,
                goods=i.goods,
                num=i.num,
                buy_money=i.goods.price

            )
        sum_money=get_cart_money(cart_items)
        # 清空购物车商品
        cart_items.delete()
        data={
            "sum_money":sum_money,
            "order":order
        }
        return render(req,"order/order_detail.html",data)