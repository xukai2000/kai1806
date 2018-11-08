from django.contrib.auth.models import AbstractUser
from django.db import models
# Create your models here.
class MyUser(AbstractUser):
    email = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="邮箱"
    )
    address = models.CharField(
        max_length=251,
        verbose_name="地址"
    )
    phone = models.CharField(
        max_length=13,
        verbose_name="手机号",
        null=True
    )
    icon=models.ImageField(
        upload_to="icons",
        null=True
    )

class BaseData(models.Model):
    img = models.CharField(
        max_length=251
    )
    name = models.CharField(
        max_length=40
    )
    trackid = models.CharField(
        max_length=30
    )

    class Meta:
        abstract = True

class Wheel(BaseData):
    class Meta:
        db_table = "axf_wheel"

class Nav(BaseData):
    class Meta:
        db_table="axf_nav"
#必买商品
class MustBuy(BaseData):
    class Meta:
        db_table = "axf_mustbuy"
# 遍历店
class Shop(BaseData):
    class Meta:
        db_table="axf_shop"

class MainShow(BaseData):
    categoryid = models.CharField(
        max_length=100
    )
    brandname = models.CharField(
        max_length=100
    )

    img1 = models.CharField(
        max_length=255
    )
    childcid1 = models.CharField(
        max_length=100
    )
    productid1 = models.CharField(
        max_length=100
    )
    longname1 = models.CharField(
        max_length=100
    )
    price1 = models.CharField(
        max_length=100
    )
    marketprice1 = models.CharField(
        max_length=100
    )

    img2 = models.CharField(
        max_length=255
    )
    childcid2 = models.CharField(
        max_length=100
    )
    productid2 = models.CharField(
        max_length=100
    )
    longname2 = models.CharField(
        max_length=100
    )
    price2 = models.CharField(
        max_length=100
    )
    marketprice2 = models.CharField(
        max_length=100
    )
    img3 = models.CharField(
        max_length=255
    )
    childcid3 = models.CharField(
        max_length=100
    )
    productid3 = models.CharField(
        max_length=100
    )
    longname3 = models.CharField(
        max_length=100
    )
    price3 = models.CharField(
        max_length=100
    )
    marketprice3 = models.CharField(
        max_length=100
    )

    class Meta:
        db_table = "axf_mainshow"

class Goods(models.Model):
    productid = models.CharField(
        max_length=20
    )
    productimg = models.CharField(
        max_length=200
    )
    productname = models.CharField(
        max_length=200,
        null=True
    )
    productlongname = models.CharField(
        max_length=200
    )
    isxf = models.BooleanField(
        default=0
    )
    pmdesc = models.BooleanField(
        default=0
    )
    specifics = models.CharField(
        max_length=20
    )
    price = models.FloatField()
    marketprice = models.FloatField()
    categoryid = models.IntegerField()
    childcid = models.IntegerField()
    childcidname = models.CharField(
        max_length=10
    )
    dealerid = models.CharField(
        max_length=20
    )
    storenums = models.IntegerField()
    productnum = models.IntegerField()

    def __str__(self):
        return str(self.price)

    class Meta:
        db_table = "axf_goods"

class GoodsTypes(models.Model):
    typeid = models.CharField(
        max_length=40
    )
    typename = models.CharField(
        max_length=10
    )
    childtypenames = models.CharField(
        max_length=200,
    )
    typesort = models.IntegerField()

    class Meta:
        db_table = "axf_foodtypes"

class Cart(models.Model):
    user=models.ForeignKey(
        MyUser
    )
    goods=models.ForeignKey(
        Goods
     )
    num=models.IntegerField(
        default=1
    )
    create_time=models.DateTimeField(
        auto_now_add=True
    )
    update_time=models.DateTimeField(
        auto_now=True
    )
    is_selected=models.BooleanField(
        default=True
    )
    class Meta:
        verbose_name="购物车"
        index_together=["user","goods"]

class Order(models.Model):
    ORDER_STATUS=(
        (1,"待付款"),
        (2,"已付款"),
        (3,"已发货"),
        (4,"已收货"),
        (5,"待评价"),
        (6,"已评价")
    )
    user=models.ForeignKey(
        MyUser
    )
    creae_time=models.DateTimeField(
        auto_now_add=True

    )
    status=models.IntegerField(
        choices=ORDER_STATUS,
        default=1
    )

class OrderItem(models.Model):
    order=models.ForeignKey(
        Order
    )
    goods=models.ForeignKey(
        Goods
    )
    num=models.IntegerField(
        verbose_name="数量"

    )
    buy_money=models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
