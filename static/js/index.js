$(function () {
    // 判断是否登录
    $.get('http://127.0.0.1:5000/check_login', {},
        function (data) {
            console.log(data);
            if (data['login'] === false) {
                // $('#show_login_reg').show();
                // $('#index_img').css('height', '71%');
            } else {
                // $('#login_register').hide();
                // $('#info_box').attr('class', 'col-lg-12');
                // $('#info_box').css('font-size', '20px');
            }
        }
    );

    // $("#reg_submit").click(function () {
    //     const name = $("#name").val();
    //     const password = $("#password").val();

    //     console.log(name);
    //     console.log(password);

    //     if ((name === undefined) || (password === undefined) || (name === '') || (password === '')) {
    //         alert('字段不能为空！');
    //         return
    //     }

    //     // 获取时间
    //     $.get('127.0.0.1:5000/register/' + name + '/' + password, {},
    //         function (data) {
    //             alert(data['info'])
    //         }
    //     );
    // });

    // $("#login_submit").click(function () {
    //     const name = $("#name").val();
    //     const password = $("#password").val();

    //     console.log(name);
    //     console.log(password);

    //     if ((name === undefined) || (password === undefined) || (name === '') || (password === '')) {
    //         alert('login_submit字段不能为空！');
    //         return
    //     }

    //     $.get('http://127.0.0.1:5000/login/' + name + '/' + password, {},
    //         function (data) {
    //             alert(data['info']);
    //             if (data['status'] == 'ok') {
    //                 window.location.href = "/"

    //             }
    //         }
    //     );

    // });
});