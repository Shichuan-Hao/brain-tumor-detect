$(function () {
    $('#nav-online-check').click(function () {
        // 判断是否登录
        $.get('http://127.0.0.1:5000/check_login', {},
            function (data) {
                if (data['login'] === false) {
                    window.location.href = "/login"
                }
            }
        );
    })

    $('#body-online-check').click(function () {
        // 判断是否登录
        $.get('http://127.0.0.1:5000/check_login', {},
            function (data) {
                if (data['login'] === false) {
                    window.location.href = "/login"
                }
            }
        );
    })

    
    $('#nav-logout').click(function () {
        // 判断是否登录
        $.get('http://127.0.0.1:5000/logout', {},
            function (data) {
                console.log(data['login'])
                if (data['login'] === false) {
                    window.location.href = "/"
                }
            }
        );
    })

    // 判断是否登录
    $.get('http://127.0.0.1:5000/check_login', {},
        function (data) {
            if (data['login'] === false) {
                // $('#show_login_reg').show();
                // $('#index_img').css('height', '71%');
                $('#nav-logout').hide();
                $('#nav-user-info').hide();
                $('#nav-login').show();

            } else {
                $('#nav-logout').show()
                $('#nav-user-info').show()
                $('#nav-login').hide();
                // $('#info_box').attr('class', 'col-lg-12');
                // $('#info_box').css('font-size', '20px');
            }
        }
    );

});