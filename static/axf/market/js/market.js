var type_dowm = true;
var sort_dowm = true;

$(function () {
    // 给全部类型添加点击事件
    $("#all_type").click(all_type_event);
    $("#c_control").click(all_type_event);

    $("#all_sort").click(all_sort_event);
    $("#s_control").click(all_sort_event);
    $(".subShopping").click(function () {
        $current_bt = $(this);
        //获取点击的那个商品的数据
        var g_id = $current_bt.attr("g_id");
        if ($current_bt.next().html() == "0") {
            return;
        }

        console.log(g_id)
        $.ajax({
            "url": "/axf/cart_api",
            //判断当前显示的是不是0

            data: {
                g_id: g_id,
                type: "sub"
            },
            method: "post",
            success: function (res) {
                console.log(res);
                if (res.code == 1) {
                    $current_bt.next().html(res.data)
                }
                if (res.code == 2) {
                    window.open(res.data, target = "_self")
                }

            }
        });
    })
    //加操作
    $(".addShopping").click(function () {
        $current_bt = $(this);
        //获取点击的那个商品的数据
        var g_id = $current_bt.attr("g_id");
        console.log(g_id)
        $.ajax({
            "url":"/axf/cart_api",
            data: {
                g_id: g_id,
                type: "add"
            },
            method: "post",
            success: function (res) {
                console.log(res);
                if (res.code == 1) {
                    $current_bt.prev().html(res.data)
                }
                if (res.code == 2) {
                    window.open(res.data, target = "_self")
                }

            }
        });
    })
})

function all_type_event() {
    $("#c_control").toggle()
    var type_span = $("#all_type").find("span").find("span");
    if (type_dowm == true) {
        //如果是向下的状态 那改变原有的类样式 修改状态值
        type_span.removeClass("glyphicon glyphicon-chevron-down").addClass("glyphicon glyphicon-chevron-up");
        type_dowm = false;
    } else {
        type_span.removeClass("glyphicon glyphicon-chevron-up").addClass("glyphicon glyphicon-chevron-down");
        type_dowm = true;
    }
}

function all_sort_event() {
    $("#s_control").toggle()
    var type_span = $("#all_sort").find("span").find("span");
    if (sort_dowm == true) {
        //如果是向下的状态 那改变原有的类样式 修改状态值
        type_span.removeClass("glyphicon glyphicon-chevron-down").addClass("glyphicon glyphicon-chevron-up");
        sort_dowm = false;
    } else {
        type_span.removeClass("glyphicon glyphicon-chevron-up").addClass("glyphicon glyphicon-chevron-down");
        sort_dowm = true;
    }
}