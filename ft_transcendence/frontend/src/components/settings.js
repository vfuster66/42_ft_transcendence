import { createQRcode, display_qrcode } from './identificator.js';
import { getCookie } from '../main.js';
import { get_text_lang } from "../assets/langues/get_text_lang.js";

export function get_player_infos_settings() {
	$.ajax({
		url: '/api/get-session/',  // URL of your Django view
		type: 'GET',
		success: function(data) {
			if (data.error){
				return;
			}
			document.getElementById('change-firstname').value = data.first_name;
			document.getElementById('change-email').value = data.email;
			if (data.img)
			{
				document.getElementById('player-image').src = data.img;
				document.getElementById('change-image').src = data.img;
			}
			else
				document.getElementById('player-image').src = "assets/anonymous-icon.png";
			createQRcode();
		},
		error: function(xhr, status, error) {
		}
	});
}

export function display_avatar()
{
    var avatardisp = document.getElementById("avatar-container");
	var titledisp = document.getElementById("title-change");
	var photodisp = document.getElementById("change-image");

    var inputfile = document.getElementById("input-file");
	if (avatardisp.classList.contains("hidden")) {
        avatardisp.classList.remove("hidden");
        titledisp.classList.add("hidden");
        photodisp.classList.add("hidden");

        inputfile.value = 'Close';
	} else {
        avatardisp.classList.add("hidden");
        inputfile.value = 'Change profile image';
		titledisp.classList.remove("hidden");
        photodisp.classList.remove("hidden");
	}
};



export function submitNewImg(image) {
	// console.log(image);
    $.ajax({
        url: '/api/change-user-img/',
        type: 'POST',
        data: {
            img: image,
        },
        beforeSend: function(xhr) {
            xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
        },
        success: function(data) {
            if (data.error) {
                return;
            }
        },
        error: function(xhr, status, error) {
        }
    });
}

window.addEventListener('load', (event) => {
    var avatars = document.querySelectorAll('.avatar');
	var image = document.getElementById('change-image');

    avatars.forEach(function(avatar) {
        avatar.addEventListener('click', function(event) {
            event.preventDefault();
            var avatarValue = this.dataset.value;
			image.setAttribute('src', avatarValue);
            submitNewImg(avatarValue);
			// console.log(avatarValue);
			display_avatar();
			document.getElementById('profil-btn-img').src = avatarValue;
        });
    });
});




export function submitNewInfo() {
    // Récupérer les nouvelles informations de l'utilisateur
    var newEmail = document.getElementById('change-email').value;
    var newFirstname = document.getElementById('change-firstname').value;
	// console.log(newEmail);
    // Vérifier si les champs sont vides
    if (newEmail == "") {
        document.getElementById('change-email').style.backgroundColor = "#fe7f7f";
        document.getElementById('change-email').focus();
        return;
    }
	var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    var emailTest = re.test(String(newEmail).toLowerCase());
	if (newEmail == "" || !emailTest) {
		document.getElementById('change-email').style.backgroundColor = "#fe7f7f"; email.focus(); return;
	}
    if (newFirstname.length <= 3) {
        document.getElementById('change-firstname').style.backgroundColor = "#fe7f7f";
        document.getElementById('change-firstname').focus();
        return;
    }

    $.ajax({
        url: '/api/change-user-info/',  // URL de votre vue Django pour la mise à jour des informations de l'utilisateur
        type: 'POST',
        data: {
            email: newEmail,
            first_name: newFirstname,
        },
        beforeSend: function(xhr) {
            xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
        },
        success: function(data) {
            if (data.error) {
				get_text_lang('update-fail').then(text => {
					document.getElementById('popup-text').innerText = text;
					document.getElementById('popup-window').classList.add('active');
				});
                return;
            }
			get_text_lang('update-success').then(text => {
				document.getElementById('popup-text').innerText = text;
				document.getElementById('popup-window').classList.add('active');
			});
        },
        error: function(xhr, status, error) {
            // Gérer les erreurs
        }
    });
}


export function changePassword() {
	// console.log("Change pass");

    var password = document.getElementById('change-password');
	var password2 = document.getElementById('change-password-repeat');

	if (password.value.length < 8 || password.value == "") {
		document.getElementById('password-strength').style.display = "";
		password.style.backgroundColor = "#fe7f7f"; password.focus(); return;
	} else {
		document.getElementById('password-strength').style.display = "none";
	}
	if (password2.value != password.value) {
		password2.style.backgroundColor = "#fe7f7f"; password2.focus(); return;
	}

	var shaPassword = sha256(password.value);
	// Make AJAX request to retrieve session data
	$.ajax({
		url: '/api/change-password/',  // URL of your Django view
		type: 'POST',
		data: {
			password: shaPassword,
		},
		beforeSend: function(xhr) {
			xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
		},
		success: function(data) {
			if (data.error) {
				get_text_lang('pass-error').then(text => {
					document.getElementById('popup-text').innerText = text;
					document.getElementById('popup-window').classList.add('active');
				});
				return;
			}
			get_text_lang('pass-changed').then(text => {
				document.getElementById('popup-text').innerText = text;
				document.getElementById('popup-window').classList.add('active');
			});
			// console.log("Password changed");
		},
		error: function(xhr, status, error) {
		}
	});
};
