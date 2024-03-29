import { getCookie } from "../main.js";
import { showF2Apopup } from "./identificator.js";

export function showMultiplayer(){
	if (document.getElementById('multi-window').classList.contains('active'))
		return;
	document.getElementById('multi-window').classList.add('active');
	if (document.querySelectorAll('.multi-content form').length === 0)
		multiAddPlayer();
}

export function hideMultiplayer(){
	document.getElementById('multi-window').classList.remove('active');
}

export function handlePlayerSubmit(playerCount){
	if (document.getElementById('submit-p' + playerCount).value === 'Login') {
		loginNewPlayer(playerCount);
	} else {
		logoutPlayer(playerCount);
	}
}

$(document).ready(function() {
    $.ajax({
        url: '/api/reset-multi/',
        type: 'GET',
        success: function(data) {
		}
	});
});

export function get_multi_session_data(){
	// console.log("fonction get_multi appelee");
	$.ajax({
		url: '/api/get_multi_session_data/',
		type: 'GET',
		success: function(data) {
			if (data.error){
				console.error("Error: ", data.error);
				reject(data.error);
				return;
			}
			// console.log("requete ajax reussie");
			let players = data.players;
			for (let i = 0; i < players.length; i++) {
				let user = players[i].login;
				let score = players[i].score;
				let img = players[i].img;
			}
			// console.log("players :", players);
			return(players);
		},
		error: function(error) {
			console.error('Error retrieving session data:', error);
			reject(error);
		}
	});
}


function removeUserFromTabs(username){
	$.ajax({
		url: '/api/get_multi_session_data/',
		type: 'GET',
		success: function(data) {
			// console.log(data);
			// remove one tab
			let rm_tab = document.getElementById('mp-user-' + username);
			rm_tab.classList.remove('active');
			setTimeout(() => rm_tab.remove(), 500);

			// update the position of the remaining tabs
			let players = data.players;
            for (let i = 0; i < players.length; i++) {
                let user = players[i].login;
                let mp_win = document.getElementById('mp-user-' + user);
                if (mp_win) {
                    setTimeout(() => {
                        mp_win.style.top = 160 + 75 * i + 'px';
                    }, 500);
                }
            }
		},
	});
}

function logoutPlayer(playerCount){
	$.ajax({
		url: '/api/multi-logout/',
		type: 'POST',
		data: {	no_player: playerCount - 2},
		beforeSend: function(xhr) {	xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));},
		success: function(data) {
			// console.log(data);
			var username = document.getElementById('login-p' + playerCount).value;
			if (document.querySelectorAll('.multi-content form').length === 1) {	// on ne supprime pas le dernier form, on le reset
				document.getElementById('login-p2').value = "";
				document.getElementById('pass-p2').value = "";
				document.getElementById('login-p2').disabled = false;
				document.getElementById('pass-p2').disabled = false;
				document.getElementById('submit-p2').value = 'Login';
				document.getElementById('submit-p2').style.backgroundColor = "";
				document.getElementById('login-p2').style.backgroundColor = "";
				document.getElementById('pass-p2').style.backgroundColor = "";
				document.getElementById('login-p2').focus();
				document.getElementById('add-player-btn').disabled = true;
				document.getElementById('add-player-btn').classList.add('disabled');
			} else {
				document.getElementById('form-p' + playerCount).remove();

				// Obtenir tous les formulaires
				let forms = document.querySelectorAll('[id^="form-p"]');
				// Mettre à jour les ID des joueurs restants
				for (let i = 0; i < forms.length; i++) {
					let playerID = i + 2;
					forms[i].id = 'form-p' + playerID;

					let loginInput = document.getElementById('login-p' + (playerID + 1));
					if (loginInput) loginInput.id = 'login-p' + playerID;

					let passwordInput = document.getElementById('pass-p' + (playerID + 1));
					if (passwordInput) passwordInput.id = 'pass-p' + playerID;

					let submitInput = document.getElementById('submit-p' + (playerID + 1));
					if (submitInput){
						submitInput.id = 'submit-p' + playerID;
						submitInput.onclick = () => handlePlayerSubmit(playerID);
					}

					let label = forms[i].querySelector('label');
					if (label) label.textContent = 'Player ' + playerID;
				}
			}
			removeUserFromTabs(username);
		},
	});
}

function loginNewPlayer(playerCount){
	var loginBox = document.getElementById('login-p' + playerCount);
	var passBox = document.getElementById('pass-p' + playerCount);

	if (loginBox.value == "") {
		loginBox.style.backgroundColor = "#fe7f7f";
		loginBox.focus();
		return;
	}
	if (passBox.value == "") {
		passBox.style.backgroundColor = "#fe7f7f";
		passBox.focus();
		return;
	}

	var allLoginBoxes = document.querySelectorAll('[id^="login-p"]');
    for (var i = 0; i < allLoginBoxes.length; i++) {
        if (allLoginBoxes[i] !== loginBox && allLoginBoxes[i].value === loginBox.value) {
			get_text_lang('login_used').then(text => alert(text));
            return;
        }
    }

	var shaPassword = sha256(passBox.value);

	$.ajax({
		url: '/api/multi-login/',  // URL of your Django view
		type: 'POST',
		data: {
			username: loginBox.value,
			password: shaPassword,
			no_player: playerCount
		},
		beforeSend: function(xhr) {
			xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
		},
		success: function(data) {
			if (data.error) {
				if (data.error === 'username'){
					loginBox.style.backgroundColor = "#fe7f7f";
					loginBox.classList.add('shake');
					setTimeout(function() {
						loginBox.classList.remove('shake');
					}, 1000);
				}
				else if (data.error === 'password'){
					passBox.style.backgroundColor = "#fe7f7f";
					passBox.classList.add('shake');
					setTimeout(function() {
						passBox.classList.remove('shake');
					}, 1000);
				}
				else if (data.error === 'api'){
					get_text_lang('api_error').then(text => alert(text));
				}
				else if (data.error === 'already logged'){
					get_text_lang('already_logged').then(text => alert(text));
				}
				return;
			}

			loginBox.style.backgroundColor = "#7fcf7c";
			passBox.style.backgroundColor = "#7fcf7c";

			if (data.f2a === true) {
				document.getElementById('f2a-login').innerText = loginBox.value;
				document.getElementById('f2a-score').innerText = data.score;
				document.getElementById('f2a-img').innerText = data.img;
				document.getElementById('f2a-playerId').innerText = playerCount;
				showF2Apopup("multi");
			} else {
				validatePlayerConnection(playerCount, data);
			}

		},
	});
}

function validatePlayerConnection(playerCount, data){
	var loginBox = document.getElementById('login-p' + playerCount);
	var passBox = document.getElementById('pass-p' + playerCount);

	loginBox.disabled = true;
	passBox.disabled = true;

	document.getElementById('submit-p' + playerCount).value = 'Logout';
	document.getElementById('submit-p' + playerCount).style.backgroundColor = "#d84d4d";

	if (document.querySelectorAll('.multi-content form').length < 8){
		document.getElementById('add-player-btn').disabled = false;
		document.getElementById('add-player-btn').classList.remove('disabled');
	}

	addPlayerWindow(loginBox.value, data.score, data.img, playerCount);
}

export function actions_f2a_for_multi() {
	let data = {
		username: document.getElementById('f2a-login').innerText,
		score: document.getElementById('f2a-score').innerText,
		img: document.getElementById('f2a-img').innerText
	}
	var playerCount = document.getElementById('f2a-playerId').innerText;
	validatePlayerConnection(playerCount, data);
	document.getElementById('f2a-window').classList.remove('active');
    document.getElementById('code2fa').value = "";
}

function addPlayerWindow(login, score, image, id) {
    // Créer les nouveaux éléments
    let userWindow = document.createElement('div');
    let userImage = document.createElement('img');
    let userLogin = document.createElement('div');
    let userScore = document.createElement('div');

    // Configurer les nouveaux éléments
    userWindow.id = 'mp-user-' + login;
	userWindow.className = 'mp-user-window';
	userWindow.style.top = 160 + 75 * (id - 2) + 'px';
	userWindow.addEventListener('click', function() {
		showPlayerProfile(login);
	});

    userImage.id = 'mp-user-image-' + login;
	userImage.src = image;

    userLogin.id = 'mp-user-login-' + login;
	userLogin.textContent = login;
	userLogin.classList.add('mp-user-login');

    userScore.id = 'mp-user-score-' + login;
	userScore.textContent = score;
	userScore.classList.add('mp-user-score');

    // Ajouter les nouveaux éléments à userWindow
    userWindow.appendChild(userImage);
    userWindow.appendChild(userLogin);
    userWindow.appendChild(userScore);

    // Ajouter userWindow à mp-users-main
    document.getElementById('mp-users-main').appendChild(userWindow);
	setTimeout(() => userWindow.classList.add('active'), 0);
}

export function multiAddPlayer(){
	if (document.getElementById('add-player-btn').disabled &&
		document.querySelectorAll('.multi-content form').length != 0) return;
	var playerCount = document.querySelectorAll('.multi-content form').length + 1;

	if (playerCount < 8) {
		var newPlayerId = 'p' + (playerCount + 1);

		var form = document.createElement('form');
		form.id = 'form-' + newPlayerId;
		form.onsubmit = function(event) { event.preventDefault(); };

		var label1 = document.createElement('label');
		label1.textContent = 'Player ' + (playerCount + 1);
		form.appendChild(label1);

		var input1 = document.createElement('input');
		input1.type = 'text';
		input1.id = 'login-' + newPlayerId;
		form.appendChild(input1);

		var label2 = document.createElement('label');
		label2.textContent = 'Mot de passe';
		label2.classList.add("mp-pass");
		label2.htmlFor = 'pass-' + newPlayerId;
		form.appendChild(label2);

		var input2 = document.createElement('input');
		input2.type = 'password';
		input2.id = 'pass-' + newPlayerId;
		form.appendChild(input2);

		var input3 = document.createElement('input');
		input3.type = 'submit';
		input3.id = 'submit-' + newPlayerId;
		input3.value = 'Login';
		input3.onclick = function() {
			handlePlayerSubmit(playerCount + 1);
		};
		form.appendChild(input3);

		var addButton = document.getElementById('add-player-btn');
		addButton.parentNode.insertBefore(form, addButton);

		document.getElementById('add-player-btn').disabled = true;
		document.getElementById('add-player-btn').classList.add('disabled');
	}
}

export function showPlayerProfile(login){
	if (!document.getElementById('popup-mpinfos').classList.contains('active'))
		document.getElementById('popup-mpinfos').classList.add('active');
	else
		document.getElementById('popup-mpinfos').classList.remove('active');
	// Make ajax request to get player info
	$.ajax({
		url: '/api/get-player-infos/',
		type: 'POST',
		data: { login: login },
		beforeSend: function(xhr) {
			xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
		},
		success: function(data) {
			document.getElementById('mpinfos-login').textContent = login;
			document.getElementById('mpinfos-image').src = data.img;
			document.getElementById('mpinfos-score').textContent = data.score;
			document.getElementById('mpinfos-wons').textContent = data.win_games;
			document.getElementById('mpinfos-games').textContent = data.total_games;

			// si gamesHistory n'est pas défini, on ne fait rien
			if (data.gamesHistory){
				// Récupérer l'historique des jeux et le diviser en lignes
				var gamesHistory = data.gamesHistory.trim().split('\n');
				// Prendre les 20 dernières lignes
				gamesHistory = gamesHistory.slice(Math.max(gamesHistory.length - 20, 0));
				// Récupérer le conteneur du tableau
				var tableContainer = document.getElementById('mpinfos-table-container');
				// Créer un nouveau tableau
				var table = document.createElement('table');
				// Ajouter l'en-tête du tableau
				table.innerHTML = `
					<thead>
						<tr>
							<th>Opponent</th>
							<th>Result</th>
							<th>Score</th>
						</tr>
					</thead>
				`;
				// Parcourir l'historique des jeux
				for (var i = gamesHistory.length - 1; i >= 0 ; --i) {
					// Diviser la ligne en ses composants
					var [opponent, score] = gamesHistory[i].split(' : ');
					var [playerPoints, opponentPoints] = score.split(' / ');
					// Déterminer le résultat du jeu
					var result = playerPoints > opponentPoints ? 'Won' : 'Lost';
					// Créer une nouvelle ligne de tableau
					var row = document.createElement('tr');
					// Ajouter les cellules à la ligne
					row.innerHTML = `<td>${opponent}</td><td>${result}</td><td>${score}</td>`;
					// Ajouter la ligne au tableau
					table.appendChild(row);
				}
				// Ajouter le tableau au conteneur du tableau
				tableContainer.innerHTML = '';
				tableContainer.appendChild(table);
			}
		},
	});
}

export function closeMpInfos(){
	document.getElementById('popup-mpinfos').classList.remove('active');
}
