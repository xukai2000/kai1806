from django.conf.urls import url

from myaxf.views import *

urlpatterns=[
    url(r"^home$",home,name="home"),
    url(r"^market$", market, name="market"),
    url(r"^market_with_params/(\d+)/(\d+)/(\d+)", market_with_params, name="market_with_params"),
    url(r"^cart$",cart,name="cart"),
    url(r"^mine$",mine,name="mine"),
    url(r"^register$",RegisterAPI.as_view(),name="register"),
    url(r"^login$",LoginAPI.as_view(),name="login"),
    url(r"logout$",LogoutAPI.as_view(),name="logout"),
    url(r"confirm/(.*)",confirm,name="confirm"),
    url(r"check_uname$",check_uname),
    url(r"^cart_api$",CartAPI.as_view()),
    url(r"^cart_status$",CartStatuAPI.as_view()),
    url(r"^cart_all_status$",CartAllStatusAPI.as_view()),
    url(r"^cart_item",CartItemAPI.as_view()),
    url(r"^order$",OrderAPI.as_view(),name="order")
]