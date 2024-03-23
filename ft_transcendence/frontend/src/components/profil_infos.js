export function get_player_infos() {
	$.ajax({
		url: '/api/get-session/',  // URL of your Django view
		type: 'GET',
		success: function(data) {
			if (data.error){
				console.error("Error: ", data.error);
				return;
			}

			// Update HTML content with session data
			// console.log('Session data loaded:', data);

			document.getElementById('profile-login').innerHTML = "<b>" + data.user + "</b>";
			// document.getElementById('profile-firstname').innerHTML = "<b>Prenom :</b> " + data.first_name;
			document.getElementById('profile-email').innerHTML = data.email;
			document.getElementById('profile-score').innerHTML = data.score;
			document.getElementById('profile-wons').innerHTML = data.win_games;
			document.getElementById('profile-games').innerHTML = data.total_games;
			if (data.img)
				document.getElementById('player-image').src = data.img;
			else
				document.getElementById('player-image').src = "assets/anonymous-icon.png";

			// si gamesHistory n'est pas défini, on ne fait rien
			if (data.gamesHistory){
				// Récupérer l'historique des jeux et le diviser en lignes
				var gamesHistory = data.gamesHistory.trim().split('\n');
				// Prendre les 20 dernières lignes
				gamesHistory = gamesHistory.slice(Math.max(gamesHistory.length - 20, 0));
				// Récupérer le conteneur du tableau
				var tableContainer = document.getElementById('profil-table-container');
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
		error: function(xhr, status, error) {
			// console.error('Error retrieving session data:', error);
		}
	});
}

export function get_player_name() {
    return new Promise((resolve, reject) => {
        $.ajax({
            url: '/api/get-session/',
            type: 'GET',
            success: function(data) {
                if (data.error){
                    console.error("Error: ", data.error);
                    reject(data.error);
                    return;
                }
                // console.log("data.user: ", data.user);
                resolve(data.user);
            },
            error: function(error) {
                console.error('Error retrieving session data:', error);
                reject(error);
            }
        });
    });
}
