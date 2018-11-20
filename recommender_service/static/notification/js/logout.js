
$(document).ready(function(){
	var auth_code = getCookies('auth_code');
	if(!auth_code){
    $(document).ready(function(){
    $('#logout').trigger('click');
    });
	}
    $("#logout").on("click", function(e) {
        $.ajax({
            type: "POST",
            url: "/logout/",
            csrfmiddlewaretoken: "{{ csrf_token }}",
            data: {},
            headers: {
                'Content-Type': 'application/json',

            },
            success: function() {

                document.cookie = 'auth_code=' + '' + ";path=/";
                window.location.href = window.location.origin + "/recommendation/notification/";
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {

                alert("some error " + String(errorThrown) + String(textStatus) + String(XMLHttpRequest.responseText));
            }
        });
    });
    function getCookies(name){
                var pattern = RegExp(name + "=.[^;]*")
                matched = document.cookie.match(pattern)
                if(matched){
                    var cookie = matched[0].split('=')
                    return cookie[1]
                }
                return false
    }


});
