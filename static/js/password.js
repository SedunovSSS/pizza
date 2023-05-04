$('body').on('click', '.check', function(){
    if ($(this).is(':checked')){
    $('#passw1').attr('type', 'text');
    } else {
    $('#passw1').attr('type', 'password');
    }
});