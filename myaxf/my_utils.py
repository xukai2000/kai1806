import uuid
import hashlib


def get_uuique_str():
    uuid_str = str(uuid.uuid4()).encode("utf-8")
    # 实列化
    md5 = hashlib.md5()
    # 进行加密
    md5.update(uuid_str)
    # 返回32位十六进制数据
    return md5.hexdigest()


def get_cart_money(cart_items):
    sum_money = 0
    cart_items=cart_items.filter(
        is_selected=True
    )
    for i in cart_items:
        # 单价乘商品数量
        sum_money = sum_money + i.goods.price * i.num
    return sum_money
