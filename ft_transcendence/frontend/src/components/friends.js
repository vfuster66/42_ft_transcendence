import { getCookie } from "../main.js";
import { showPlayerProfile } from "./multiplayer.js";
import { get_text_lang } from "../assets/langues/get_text_lang.js";

export function addFriend () {
	let url = new URL(window.location.href);
	let params = new URLSearchParams(url.search);
	let lang = params.get('lang') || "en";
	let friend_name = document.getElementById('add-friend-input').value;
	// console.log("Friend :" + friend_name);
	if (friend_name === '') {
		return;
	}
	$.ajax({
		url: '/api/get-session/',
		type: 'GET',
		success: function(data) {
			if (data.error) {
				console.error("Error friend getsession: ", data.error);
				return;
			}
			let user = data.user;
			if (!user) {
				return;
			}
			if (friend_name === user) {
				get_text_lang('friend-self').then(text => {
					document.getElementById('popup-text').innerText = text;
					document.getElementById('popup-window').classList.add('active');
				});
				setTimeout(function() { document.getElementById('popup-Button').focus();}, 400);
				return;
			}
			$.ajax({
				url: '/api/add-friend/',  // URL of your Django view
				type: 'POST',
				data: {
					username: user,
					friend: friend_name,
				},
				beforeSend: function(xhr) {
					xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
				},
				success: function(data) {

					if (data.error) {
						if (data.error === "not_found"){
							get_text_lang('friend-none').then(text => {
								document.getElementById('popup-text').innerText = friend_name + " " + text;
								document.getElementById('popup-window').classList.add('active');
							});
						} else if (data.error === "already_friend"){
							get_text_lang('friend-already').then(text => {
								document.getElementById('popup-text').innerText = friend_name + " " + text;
								document.getElementById('popup-window').classList.add('active');
							});
						}
						setTimeout(function() { document.getElementById('popup-Button').focus();}, 400);
					} else {
						get_text_lang('friend-added').then(text => {
							document.getElementById('popup-text').innerText = friend_name + " " + text;
							document.getElementById('popup-window').classList.add('active');
						});
						setTimeout(function() { document.getElementById('popup-Button').focus();}, 400);
						document.getElementById('add-friend-input').value = "";
						getFriendList();
					}

				},
				error: function(error) {
					console.error('Error adding friend:', error);
				}
			});
		}
	});

}

export function getFriendList() {

	$.ajax({
		url: '/api/get-session/',
		type: 'GET',
		success: function(data) {
			if (data.error) {
				console.error("Error friend getsession: ", data.error);
				return;
			}
			// friend list stored in data.friends
			let friends = data.friends;
			let friendList = document.getElementById('friends-list');
			friendList.innerHTML = '';
			for (let i = 0; i < friends.length; i++) {
				let friend = friends[i];
				let friendItem = document.createElement('li');
				friendItem.id = 'friends-' + friend.login;
				friendItem.classList.add('friends-window');
				friendItem.innerHTML = `
					<img id="friends-image-${friend.login}" src=${friend.image_link}>
					<div id="friends-login-${friend.login}" class="friends-login">${friend.login}</div>
					<div id="friends-rm-${friend.login}" class="friends-rm">X</div>
				`;
				friendList.appendChild(friendItem);

				document.getElementById(`friends-rm-${friend.login}`).addEventListener('click', function(event) {
					event.stopPropagation();
                    removeFriend(friend.login);
                });
				document.getElementById(`friends-${friend.login}`).addEventListener('click', function() {
                    showPlayerProfile(friend.login);
                });
			}

		},
		error: function(xhr, status, error) {
			console.error('Error retrieving session data:', error);
		}
	});
}

export function removeFriend(friend) {
	$.ajax({
		url: '/api/remove-friend/',  // URL of your Django view
		type: 'POST',
		data: {
			friend: friend,
		},
		beforeSend: function(xhr) {
			xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
		},
		success: function(data) {
			if (data.error) {
				console.error("Error removing friend: ", data.error);
				return;
			}
			getFriendList();
		},
		error: function(error) {
			console.error('Error removing friend:', error);
		}
	});
}

export function emptyFriendList() {
	document.getElementById('friends-list').innerHTML = '';
	document.getElementById('friends-main').classList.remove('active');
}

export function showFriendList() {
	getFriendList();
	document.getElementById('friends-main').classList.add('active');
}

