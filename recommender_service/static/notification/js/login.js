/**
 * 
 */

/** ***********login page modal rules**************** */
jQuery.validator.addMethod("_checkLoginUserName", function(user_name, element) {
	user_name = $('#user_name').val().trim();
	if (user_name.length == 0) {
		return this.optional(element) || false;
	}else {
		return this.optional(element) || true;
	}
}, function(error, element) {
	user_name1 = $('#user_name').val().trim();
	if (user_name1.length == 0) {
		return 'Empty spaces not allowed';
	}
});

jQuery.validator.addMethod("_checkLoginPassword", function(password, element) {
	password = $('#password').val().trim();
	if (password.length == 0) {
		return this.optional(element) || false;
	} else {
		return this.optional(element) || true;
	}
}, function(error, element) {
	var password1 = $('#password').val().trim();
	if (password.length == 0) {
		return 'password cannot be empty'
	}
});


$(document).ready(function() {
	/** ***************login form validation************** */
	$('#login_form').validate({
		rules : {
			username : {
				required : true,
				_checkLoginUserName : true
			},
			password : {
				required : true,
				_checkLoginPassword : true
			},
		},
		messages : {},
		submitHandler : function(form) {
			$('.loginButton').prop('disabled', 'disabled');
			$('#_loginButtonLoader').show();

            var username = form.username.value;
            var password = form.password.value;
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
                    console.log(data);
                    var token = data["Token"];
                    document.cookie = 'auth_code=' + token + ";path=/";
                    console.log(document.cookie);
                    window.location.href = window.location.origin + "/recommendation/notification/view_recommendation/";
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    //alert("some error " + String(errorThrown) + String(textStatus) + String(XMLHttpRequest.responseText));
                    alert("invalid credentials.");
                    $('.loginButton').prop('disabled', false);
                    $('#_loginButtonLoader').hide();
                }
            });

		}
	});
});