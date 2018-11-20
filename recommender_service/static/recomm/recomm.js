
        function myfunction(val){
            if(val=='similar_content')
            {
            document.getElementById('content_id').style.display='block';
            }else{
            document.getElementById('content_id').style.display='none';
            }
        }
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                function getCookie(name) {
                    var cookieValue = null;
                    if (document.cookie && document.cookie != '') {
                        var cookies = document.cookie.split(';');
                        for (var i = 0; i < cookies.length; i++) {
                            var cookie = jQuery.trim(cookies[i]);
                            // Does this cookie string begin with the name we want?
                            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                                break;
                            }
                        }
                    }
                    return cookieValue;
                }
                if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                    // Only send the token to relative URLs i.e. locally.
                    xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                }
            }
        });

        $("#recomm").on("click", function(e) {
            var user_id = document.getElementById("user_id").value;
            var content_id = document.getElementById("content_id").value;
            var bucket = document.getElementById("sel1").value;
            var token=getCookies('auth_code');
            console.log(token);
            if(token==''){
            alert("session expired.please login..");
            window.location.href = window.location.origin + "/recommendation/test/";
            }
            if(bucket=='similar_content'&& content_id=='')
            {
                alert("content_id is mandatory.");
                return;
            }
            $.ajax({
                type: "POST",
                url: "/recommendation/render/",
                csrfmiddlewaretoken: "{{ csrf_token }}",
                data:JSON.stringify({
                "user_id" :user_id,
                "content_id" : content_id,
                "recommendation_bucket": bucket,
                }),
                dataType: "json",
                dataType: "html",
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'Authorization':'Token '+token
                },
                success: function(data) {
                   $('#page_result').html(data);

                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    alert("some error " + String(errorThrown) + String(textStatus) + String(XMLHttpRequest.responseText));
                }
            });
        });

        $("#login").on("click", function(e) {
            var username = document.getElementById("username").value;
            var password = document.getElementById("password").value;
            $.ajax({
                type: "POST",
                url: "/login/",
                csrfmiddlewaretoken: "{{ csrf_token }}",
                data: JSON.stringify({
                    username: username,
                    password: password
                }),
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                success: function(data) {
                    var token = data["Token"];
                    document.cookie = 'auth_code=' + token + ";path=/";
                    console.log(document.cookie);
                    window.location.href = window.location.origin + "/recommendation/test/";
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    alert("some error " + String(errorThrown) + String(textStatus) + String(XMLHttpRequest.responseText));
                }
            });
        });
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
                    window.location.href = window.location.origin + "/recommendation/test/";
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

$(function(){
  $("#table2").tablesorter();
});
$(function(){
  $("#table1").tablesorter();
});