$('#frm_login').submit(function (e) {
    e.preventDefault();
    $.ajax({
        url: $(this).data('url'),
        type: 'POST',
        data: objectForm($(this)),
        success: function (response) {
            const time = 1500;
            showMessage(response.type, response.msg);
            reload(time);
        },
        error: function (error) {
            if ([400, 401, 405].includes(error.status)) {
                const response = error.responseJSON;
                showMessage(response.type, response.msg);
                $('#frm_login')[0].reset();
                $('#id_username').focus();
            }
        }
    });
});
