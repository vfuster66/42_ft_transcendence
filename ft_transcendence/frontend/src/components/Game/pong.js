import { draw_game_menu, draw_ingame_menu, draw_endgame_menu, draw_tournament_menu, hide_game_menu, show_hide_canvas } from './pong_menu.js';
import { update_score } from './pong_bdd.js';
import { get_player_name } from '../profil_infos.js';
import { get_multi_session_data, showMultiplayer } from '../multiplayer.js';
import { navigate } from '../nav.js';

// A faire :
// verifier la langue des phrases des ajouts js

document.addEventListener("DOMContentLoaded", function () {

	// RECUP DES INFOS JOUEUR

	let playerOneName = "Player One";

	get_player_name().then(user => {
		playerOneName = user;
	}).catch(error => {
		// console.error(error);
	});

	//CONSTANTES

    const canvas = document.getElementById("pongCanvas");
    const ctx = canvas.getContext("2d");
	let playerTwoName = canvas.dataset.playerTwo || "Player Two";
    const winnerImage = document.getElementById("winnerImage");
    const looserImage = document.getElementById("looserImage");
    const pongImage = document.getElementById("pongImage");
	const vsbutton = document.getElementById("vsbtn");
	const aibutton = document.getElementById("aibtn");
	const modbutton = document.getElementById("modbtn");
	const tourbutton = document.getElementById("tourbtn");
	const startbutton = document.getElementById("startbtn");
	const pausebutton = document.getElementById("pausebtn");
	const quitbutton = document.getElementById("quitbtn");
	const quit2button = document.getElementById("quit2btn");
	const quit3button = document.getElementById("quit3btn");
	const newgamebutton = document.getElementById("ngbtn");
	const nextbutton = document.getElementById("nextbtn");
	const paddleWidth = canvas.width / 40, paddleHeight = canvas.height / 6;
    const paddleSpeed = 8;
	const paddleSpeedAI = 9;
	const ballspeedmax = 8;
	const keyState = {};
	const brickRows = 10; // Nombre de lignes de briques
    const brickCols = 8; // Nombre de colonnes de briques
    const brickWidth = canvas.width / 60; // Largeur des briques
    const brickHeight = canvas.height / 20; // Hauteur des briques
    const brickPadding = canvas.height / 60; // Espace entre les briques
    const brickOffsetTop = canvas.height * 1 / 5; // Marge supérieure des briques
    const brickOffsetLeft = (canvas.width - (brickCols * (brickWidth + brickPadding))) / 2; // Marge gauche des briques
    const brickColors = ["#D35400", "#E67E22", "#F39C12", "#E74C3C", "#F4D03F"];

    let animationFrameId = 0;
    let gamePaused = false;
    let predict = 0;
    let selectedMode = null;
    let quarterfinal = 0;
    let semifinal = 0;
    let final = 0;
    let endtournament = false;
	let matchesquarter = [];
    let matchessemi = [];
    let matchesfinal = [];
    let push_start = 0;
    let scoreLimit = 3;
    let endgame = 0;
    let lastwinner = null;
    let paddle1 = (canvas.height - paddleHeight) / 2
    let paddle2 = (canvas.height - paddleHeight) / 2
    let lastpaddlespeed = 3;
    let score1 = 0;
    let score2 = 0;
    let lastscore = {score1: 0, score2: 0};
    let ballX;
    let ballY;
    let ballSpeedX;
    let ballSpeedY;
	resetBall();
    let bricks = []; // Tableau pour stocker les briques

	// INITIALISATION DES ELEMENTS

	//BRICKS

	// Fonction d'initialisation des briques
	function initBricks() {
		for (let c = 0; c < brickCols; c++) {
			bricks[c] = [];
			for (let r = 0; r < brickRows; r++) {
				const brickX = c * (brickWidth + brickPadding) + brickOffsetLeft;
				const brickY = r * (brickHeight + brickPadding) + brickOffsetTop;
				bricks[c][r] = { x: brickX, y: brickY, status: 1, color: brickColors[Math.floor(Math.random() * brickColors.length)] };
			}
		}
	}

	// Fonction pour dessiner les briques
	function drawBricks() {
		for (let c = 0; c < brickCols; c++) {
			for (let r = 0; r < brickRows; r++) {
				if (bricks[c][r].status === 1) {
					ctx.beginPath();
					ctx.rect(bricks[c][r].x, bricks[c][r].y, brickWidth, brickHeight);
					ctx.fillStyle = bricks[c][r].color;
					ctx.fill();
					ctx.closePath();
				}
			}
		}
	}

	// RAQUETTES

	// Dessine une raquette
	function drawPaddle(x, y) {
		ctx.fillStyle = "#F1C40F";
		ctx.fillRect(x, y, paddleWidth, paddleHeight);
	}

	// BALLE

	// Dessine la balle
	function drawBall(x, y) {
		ctx.beginPath();
		ctx.arc(x, y, 10, 0, Math.PI * 2);
		ctx.fillStyle = "#CB4335";
		ctx.fill();
		ctx.closePath();
	}

	function resetBall() {
		ballX = canvas.width / 2;
		ballY = canvas.width / 2;
		ballSpeedX = Math.random() < 0.5 ? -4 : 4;
			ballSpeedY = Math.random() * 6 - 3;
		}

	// TERRAIN

	function clearCanvas() {
		ctx.clearRect(0, 0, canvas.width, canvas.height);
	}

	function drawGoalLines() {
		// Dessine les lignes de but
		ctx.beginPath();
		ctx.moveTo(5, 0);
		ctx.lineTo(5, canvas.height);
		// Définir le motif de pointillé
		ctx.setLineDash([20, 10]); // [longueur du trait, longueur de l'espace]
		ctx.lineWidth = 5;
		ctx.strokeStyle = "#F7DC6F";
		ctx.stroke();
		ctx.closePath();
		ctx.beginPath();
		ctx.moveTo(canvas.width - 5, 0);
		ctx.lineTo(canvas.width - 5, canvas.height);
		ctx.stroke();
		ctx.closePath();
		ctx.setLineDash([]);
	}

	function drawMiddleLine() {
		// Dessine la ligne au milieu du terrain
		ctx.beginPath();
		ctx.moveTo(canvas.width / 2, 0);
		ctx.lineTo(canvas.width / 2, canvas.height);
		ctx.strokeStyle = "#F7DC6F";
		ctx.stroke();
		ctx.closePath();
	}

	function drawCourt() {
		drawGoalLines();
		drawMiddleLine();
	}

	function displayScoresAndNames() {
		// Affiche le score en haut de l'écran
		ctx.font = "900 100px Noto Sans";
		ctx.fillStyle = "#ffe6b3";
		const score1Metrics = ctx.measureText(score1);
		ctx.fillText(score1, canvas.width / 2 - 25 - score1Metrics.width, 80);
		ctx.fillText(score2, canvas.width / 2 + 25, 80);
		ctx.font = "900 20px Noto Sans";
		ctx.fillStyle = "#ffe6b3";
		const playerOneMetrics = ctx.measureText(playerOneName);
		const playerTwoMetrics = ctx.measureText(playerTwoName);
		ctx.fillText(playerOneName, canvas.width / 4 - playerOneMetrics.width / 2, 20);
		ctx.fillText(playerTwoName, canvas.width * 3 / 4 - playerTwoMetrics.width / 2, 20);
	}

	function drawPaddles() {
		// Dessine les raquettes...
		drawPaddle(10, paddle1);
		drawPaddle(canvas.width - paddleWidth - 10, paddle2);
	}

	function showStartGameMessage() {
		// Affiche le message "Press ENTER to start game"...
		const text = "Press ENTER to start game";
		ctx.font = "900 50px Noto Sans";
		const textMetrics = ctx.measureText(text);
		const textWidth = textMetrics.width;
		const ascent = textMetrics.actualBoundingBoxAscent;
		const descent = textMetrics.actualBoundingBoxDescent;
		const textHeight = ascent + descent;
		ctx.fillStyle = "#ffe6b3";
		const padding = 10;
		ctx.fillRect((canvas.width - textWidth) / 2 - padding, (canvas.height - textHeight) / 2 - padding, textWidth + 2 * padding, textHeight + 2 * padding);
		ctx.fillStyle = "#000";
		ctx.fillText(text, (canvas.width - textWidth) / 2, (canvas.height + ascent - descent) / 2);
	}

	function handleBallMovementAndCollisions() {
		drawBall(ballX, ballY);
		ballX += ballSpeedX;
		ballY += ballSpeedY;
		if (ballY + 10 > canvas.height || ballY - 10 < 0) {
			ballSpeedY = -ballSpeedY;
		}
		// Gestion de la collision avec la raquette droite (paddle1)
		if (isCollision(ballX, ballY, 10, paddle1, paddleWidth, paddleHeight)) {
			ballSpeedX = -ballSpeedX;
			const paddleCenter = paddle1 + paddleHeight / 2;
			const ballRelativeY = ballY - paddleCenter;
			ballSpeedY = ballRelativeY * 0.05;
			ballSpeedX = Math.abs(ballSpeedX) + Math.abs(ballRelativeY * 0.05);
			if (ballSpeedY > ballspeedmax)
				ballSpeedY = ballspeedmax;
			if (ballSpeedX > ballspeedmax)
				ballSpeedX = ballspeedmax;
		}

		// Gestion de la collision avec la raquette droite (paddle2)
		if (isCollision(ballX, ballY, canvas.width - 30, paddle2, paddleWidth, paddleHeight)) {
			ballSpeedX = -ballSpeedX;
			const paddleCenter = paddle2 + paddleHeight / 2;
			const ballRelativeY = ballY - paddleCenter;
			ballSpeedY = ballRelativeY * 0.05;
			ballSpeedX = -Math.abs(ballSpeedX) - Math.abs(ballRelativeY * 0.05);
			if (ballSpeedY > ballspeedmax)
				ballSpeedY = ballspeedmax;
			if (ballSpeedX > ballspeedmax)
				ballSpeedX = ballspeedmax;
		}
		// console.log("speedX: " + ballSpeedX + ", speedY: " + ballSpeedY);

		// Vérifie si la balle a traversé les raquettes (marque un point)
		if (ballX <= 0 || ballX > canvas.width) {
			if (ballX <= 0)
				score2++;
			else
				score1++;
			// Réinitialise la position de la balle au centre
			resetBall();
		}
	}

	function handleEndGame() {
		// Gère la logique de fin de jeu, affiche le menu de fin de jeu ou le menu du tournoi...
		hide_game_menu();
		if (selectedMode === "tournament")
		{
			if (endtournament)
				draw_endgame_menu();
			else
				draw_tournament_menu();
			return;
		}
		else
			draw_endgame_menu();
	}
	
	function requestNextFrame(value) {
		// Demande la prochaine frame d'animation basée sur l'état du jeu (endgame, push_start, etc.)
		if (endgame === 0 && push_start === 1) {
			animationFrameId = requestAnimationFrame(value);
		} else if (endgame === 1) {
			handleEndGame();
		}
	}

	function drawGameElement()
	{
		if ((!gamePaused) && (document.getElementById("pongCanvas").style.display == 'none'))
			document.getElementById("pongCanvas").style.display = '';
		// Efface le canvas
		clearCanvas();
		drawCourt();
		displayScoresAndNames();
		drawPaddles();
		hide_game_menu();
		draw_ingame_menu();
	}

	function game_loop()
	{
		if (push_start == 1) {
			handleBallMovementAndCollisions();
			updateScore();
		}
		else
			showStartGameMessage();
		updateManualPlayer();
	}
	
	function draw_pong()
	{
		drawGameElement();
		if (selectedMode === "mod") {
			drawBricks();
			checkBrickCollision();
			updateBricks();
		}
		game_loop();
		requestNextFrame(draw_pong);
	}

	function draw_pongAI()
	{
		playerTwoName = "AI";
		drawGameElement();
		game_loop();
		AIEverymilliSecond();
		requestNextFrame(draw_pongAI);
	}

	// IMAGE DRAGON

	function drawDragonBackground() {
		clearCanvas();
		ctx.drawImage(pongImage, 0, 0, canvas.width, canvas.height);
	}

	function resetGame() {
		score1 = 0;
		score2 = 0;
		resetBall();
		if (selectedMode !== "tournament")
			selectedMode = null;
		gamePaused = false;
		predict = 0;
		paddle1 = (canvas.height - paddleHeight) / 2
		paddle2 = (canvas.height - paddleHeight) / 2
		bricks = [];
		endgame = 0;
		push_start = 0;
		pausebutton.innerText = "Pause";
		initBricks();
	}

	function handleKeydown(event) {
		keyState[event.key] = true;
	}

	function handleKeyup(event) {
		keyState[event.key] = false;
	}

	function updateManualPlayer()
	{
		if (keyState["p"] && push_start == 1)
			togglePause();
		if (keyState["e"] && paddle1 > 0)
			paddle1 -= paddleSpeed;
		if (keyState["d"] && paddle1 < canvas.height - paddleHeight)
			paddle1 += paddleSpeed;
		if (keyState["ArrowUp"] && paddle2 > 0)
			paddle2 -= paddleSpeed;
		if (keyState["ArrowDown"] && paddle2 < canvas.height - paddleHeight)
			paddle2 += paddleSpeed;
	}

	function checkBrickCollision() {
		for (let c = 0; c < brickCols; c++) {
			for (let r = 0; r < brickRows; r++) {
				const brick = bricks[c][r];
				if (brick.status === 1) {
					// Coordonnées du centre de la balle
					let centerX = ballX;
					let centerY = ballY;
					// Trouver la distance entre le centre de la balle et le centre de la brique
					let dx = Math.abs(centerX - brick.x - brickWidth / 2);
					let dy = Math.abs(centerY - brick.y - brickHeight / 2);
					// Calculer la distance entre le centre de la balle et le centre de la brique
					let distX = dx - brickWidth / 2;
					let distY = dy - brickHeight / 2;
					if (distX < 0 && distY < 0) {
						// La balle touche la brique
						if (Math.abs(distX) < Math.abs(distY))
							ballSpeedX = -ballSpeedX; // Collision verticale Inversion de la direction horizontale
						else
							ballSpeedY = -ballSpeedY; // Collision horizontale Inversion de la direction verticale
						brick.status = 0; // La brique est détruite
					}
				}
			}
		}
	}

	function updateBricks() {
		let brickCount = 0;
		for (let c = 0; c < brickCols; c++) {
			for (let r = 0; r < brickRows; r++) {
				brickCount += bricks[c][r].status;
			}
		}
		if (brickCount === 0) {
			// Toutes les briques sont détruites, vous pouvez mettre en place une action spéciale ici
		}
	}

	function togglePause() {
		gamePaused = !gamePaused;
		if (gamePaused) {
			pausebutton.innerText = "Resume";
			cancelAnimationFrame(animationFrameId);
			// Affiche un message de pause sur l'écran
			ctx.font = "900 50px Noto Sans";
			const pauseText = "Paused";
			const textMetrics = ctx.measureText(pauseText);
			const textWidth = textMetrics.width;
			ctx.fillStyle = "#ffe6b3";
			ctx.fillRect((canvas.width - textWidth) / 2 - 10, canvas.height / 2 - 40, textWidth + 20, 80);
			ctx.fillStyle = "#000";
			ctx.fillText(pauseText, (canvas.width - textWidth) / 2, canvas.height / 2);
		} else {
			pausebutton.innerText = "Pause";
			if (selectedMode === "1vs1" || selectedMode === "tournament" || selectedMode === "mod")
				draw_pong();
			if (selectedMode === "1vsAI")
				draw_pongAI();
		}
	}


		function isCollision(ballX, ballY, paddleX, paddleY, paddleWidth, paddleHeight)
		{
			return (
				ballX - 10 < paddleX + paddleWidth &&
				ballX + 10 > paddleX &&
				ballY - 10 < paddleY + paddleHeight &&
				ballY + 10 > paddleY
			);
		}

		function updateScore() {
			if (score1 >= scoreLimit || score2 >= scoreLimit) {
				cancelAnimationFrame(animationFrameId);
				endgame = 1;
				push_start = 0;
				// Supprime tout du canvas
				clearCanvas();

				ctx.fillStyle = "#a791e7";
				ctx.fillRect(0, 0, canvas.width, canvas.height);
				// Affiche l'image du gagnant dans le canvas
				if (score2 > score1 && selectedMode === "1vsAI")
					ctx.drawImage(looserImage, 0, 100, canvas.width, canvas.height - 100);
				else
					ctx.drawImage(winnerImage, 0, 100, canvas.width, canvas.height - 100);
				let result = score1 - score2;
				if (result > 0) {
					// affiche un rectangle bleu en haut de lecran
					ctx.fillStyle = "#000"; // Couleur bleu
					ctx.fillRect(0, 0, canvas.width, 100);
					update_score(playerOneName, playerTwoName, result, 1, score1, score2);
					if (playerTwoName != "Player Two")
						update_score(playerTwoName, playerOneName, -result, 0, score2, score1);
				}
				else {
					// affiche un rectangle rouge en haut de lecran
					ctx.fillStyle = "#000"; // Couleur rouge
					ctx.fillRect(0, 0, canvas.width, 100);
					update_score(playerOneName, playerTwoName, result, 0, score1, score2);
					if (playerTwoName != "Player Two")
						update_score(playerTwoName, playerOneName, -result, 1, score2, score1);
				}

				// Affiche le score en haut de l'écran
				ctx.font = "900 80px Noto Sans";
				ctx.fillStyle = "#ffe6b3";
				const score1Metrics = ctx.measureText(score1);
				ctx.fillText(score1, canvas.width / 2 - 25 - score1Metrics.width, 80);
				ctx.fillText(score2, canvas.width / 2 + 25, 80);
				ctx.font = "900 40px Noto Sans";
				ctx.fillStyle = "#ffe6b3";

				const playerOneMetrics = ctx.measureText(playerOneName);
				const playerTwoMetrics = ctx.measureText(playerTwoName);
				const AIMetrics = ctx.measureText("AI");
				ctx.fillText(playerOneName, canvas.width / 4 - playerOneMetrics.width / 2, 60);
				if (selectedMode === "1vsAI")
					ctx.fillText("AI", canvas.width * 3 / 4 - AIMetrics.width / 2, 60);
				else
					ctx.fillText(playerTwoName, canvas.width * 3 / 4 - playerTwoMetrics.width / 2, 60);

				// Dessiner le texte des boutons
				ctx.font = "900 30px Noto Sans";
				ctx.fillStyle = "#ffe6b3";
				// console.log("selectedMode2 : ", selectedMode, " endtournament : ", endtournament);
			}
		}

		function get_multi_session_data() {
			return new Promise((resolve, reject) => {
				$.ajax({
					url: '/api/get_multi_session_data/',
					type: 'GET',
					success: function(data) {
						if (data.error) {
							reject("Error retrieving data: ", data.error);
							return;
						}
						resolve(data.players);
					},
					error: function(error) {
						reject("Error retrieving session data", error);
					}
				});
			});
		}

		vsbutton.addEventListener("click", async (event) => {
			try {
				const opponents = await get_multi_session_data();
				// Supposons que vous voulez défier le premier adversaire retourné par l'API
				if (opponents && opponents.length === 1) {
					const opponentName = opponents[0].login; // Choisir le premier adversaire pour l'exemple
					playerTwoName = opponentName;
				} else {
					console.error("No opponents found.");
				}
				if (opponents.length == 0)
				{
					alert("With who you want play ? Please log other participants.");
					showMultiplayer();
				}
				else
				{
					// console.log(playerTwoName);
					selectedMode = "1vs1";
					push_start = 0;
					draw_pong();
				}
			} catch (error) {
				console.error("An error occurred:", error);
			}
		});


		aibutton.addEventListener("click", (event) => {
			selectedMode = "1vsAI";
			draw_pongAI();
		});

		modbutton.addEventListener("click", (event) => {
			selectedMode = "mod";
			push_start = 0;
			draw_pong();
		});

		tourbutton.addEventListener("click", async (event) => {
			try {
				let players = await get_multi_session_data();
				selectedMode = "tournament";
				players = [...players.map(player => player.login)];
				if (!players.includes(playerOneName))
					players.unshift(playerOneName);
				let numParticipants = players.length;
				// console.log(players, numParticipants);

				// S'il n'y a pas assez de joueurs, demandez d'en ajouter manuellement
				if (numParticipants < 3) {
					get_text_lang('not_enough_players').then(text => alert(text));
					showMultiplayer();
				} else {
					if (numParticipants > 4)
					{
						for (let i = 0; i < 8 - numParticipants; i++)
							players.push("exempt");
						quarterfinal = 1;
						semifinal = 0;
						final = 0;
					} else {
						for (let i = 0; i < 4 - numParticipants; i++)
							players.push("exempt");
						quarterfinal = 0;
						semifinal = 1;
						final = 0;
					}
					startTournament(players);
				}
			} catch (error) {
				console.error("Erreur lors de la récupération des données:", error);
			}
		});

		startbutton.addEventListener("click", async (event) => {
			if (selectedMode != "tournament" && selectedMode != "1vsAI")
			{
				try {
					const opponents = await get_multi_session_data();
					// Supposons que vous voulez défier le premier adversaire retourné par l'API
					if (opponents && opponents.length > 0) {
						const opponentName = opponents[0].login; // Choisir le premier adversaire pour l'exemple
						playerTwoName = opponentName;
					} else {
						console.error("No opponents found.");
					}
					if (opponents.length == 0 && (selectedMode == '1vs1' || selectedMode == "mod"))
					{
						alert("Something get wrong, where is player two ? Please log other participants.");
						showMultiplayer();
					}
					else
					{
						push_start = 1;
						document.getElementById("quitbtn").innerText = "Restart";
						draw_pong();
					}
				} catch (error) {
					console.error("An error occurred:", error);
				}
			}
			
			if (selectedMode === "tournament")
			{
				push_start = 1;
				document.getElementById("quitbtn").innerText = "Restart";
				draw_pong();
			}
			if (selectedMode === "1vsAI")
			{
				push_start = 1;
				document.getElementById("quitbtn").innerText = "Restart";
				draw_pongAI();
			}
		});


		pausebutton.addEventListener("click", (event) => {
			togglePause();
		});

		quitbutton.addEventListener("click", (event) => {
			endgame = 0; // Assurez-vous que endgame est réinitialisé correctement
			push_start = 0; // Le jeu n'est plus en cours, donc push_start est remis à 0
			gamePaused = false; // Assurez-vous que le jeu n'est pas en état de pause
			document.getElementById("quitbtn").innerText = "Quit";

			// Masquer le canvas du jeu
			document.getElementById("pongCanvas").style.display = 'none';

			// Si le mode de jeu était 'tournament', alors nettoyer le tournoi
			if (selectedMode === "tournament") {
				cleartournament();
			}

			// Affichage du menu de jeu principal et réinitialisation du jeu
			hide_game_menu();
			resetGame();
			draw_game_menu();

			// Considérer l'ajout d'un log pour le débogage
			// console.log("Jeu quitté, retour au menu principal.");
		});

		quit2button.addEventListener("click", (event) => {
			// console.log("quit2");
			// console.log("avant endgame : " + endgame + " push_start : " + push_start);
			if (endgame !== 1)
				endgame = 1;
			if (push_start !== 0)
				push_start = 0;
			// console.log("apres endgame : " + endgame + " push_start : " + push_start);
			document.getElementById("pongCanvas").style.display = 'none';
			endgame = 1;
			push_start = 0;
			// console.log("quit2: push_start : " + push_start + "endagme : " + endgame)
			if (selectedMode === "tournament")
				cleartournament();
			hide_game_menu();
			draw_game_menu();
			resetGame();
		});

		quit3button.addEventListener("click", (event) => {
			// console.log("quit3");
			// console.log("avant endgame : " + endgame + " push_start : " + push_start);
			if (endgame !== 1)
				endgame = 1;
			if (push_start !== 0)
				push_start = 0;
			// console.log("apres endgame : " + endgame + " push_start : " + push_start);
			document.getElementById("pongCanvas").style.display = 'none';
			endgame = 1;
			push_start = 0;
			// console.log("quit3: push_start : " + push_start + "endagme : " + endgame)
			if (selectedMode === "tournament")
				cleartournament();
			hide_game_menu();
			draw_game_menu();
			resetGame();
		});

		newgamebutton.addEventListener("click", (event) => {
			if (endgame == 1 && selectedMode !== "tournament")
			{
				document.getElementById("pongCanvas").style.display = 'block';
				hide_game_menu();
				draw_game_menu();
				resetGame();
				drawDragonBackground();
			}
		});

		nextbutton.addEventListener("click", (event) => {
			if (selectedMode === "tournament")
			{
				if (endgame == 1)
				{
					if (score1 > score2)
						lastwinner = playerOneName;
					else
						lastwinner = playerTwoName;
					updatetournament();
					lastscore[score1] = score1;
					lastscore[score2] = score2;
					resetGame();
					if (endtournament)
					{
						matchesfinalended();
						cleartournament();
					}
					else
						drawtournament();
				} else {
            		draw_pong();
				}
			}
		})

	// AI

		function AIEverySecond() {
			setInterval(function() {
				if (selectedMode === "1vsAI" && push_start == 1)
					updateAI();
			}, 1000); // 1000 millisecondes équivalent à 1 seconde
		}

		function AIEverymilliSecond() {
			// setInterval(function() {
				if (selectedMode === "1vsAI") {
					if (lastpaddlespeed == 1 && paddle2 < canvas.height - paddleHeight && paddle2 < predict)
						paddle2 += paddleSpeedAI;
					if (lastpaddlespeed == -1 && paddle2 > 0 && paddle2 > predict)
						paddle2 -= paddleSpeedAI;
				}
			// }, 10); // 1000 millisecondes équivalent à 1 seconde
		}

		function updateAI() {
			// Logique de mouvement de base

			// Anticipation de la trajectoire de la balle
			if (ballSpeedX > 0) {
				// Prédiction du point d'intersection de la balle avec la ligne de l'IA
				const predictedIntersectionY = calculatePredictedIntersection();

				// Ajustement de la position en fonction de la prédiction
				if (predictedIntersectionY > paddle2 + paddleHeight / 2 && paddle2 < canvas.height - paddleHeight) {
					predict = predictedIntersectionY - paddleHeight / 2;
					lastpaddlespeed = 1;
				}
				if (predictedIntersectionY < paddle2 + paddleHeight / 2 && paddle2 > 0) {
					predict = predictedIntersectionY - paddleHeight / 2;;
					lastpaddlespeed = -1;
				}
			}
		}

		function calculatePredictedIntersection() {
			// Calcule le temps estimé avant que la balle n'atteigne la position de l'IA
			const estimatedTime = (canvas.width - ballX) / ballSpeedX;

			// Calcule la position Y de la balle à ce moment-là
			const predictedY = ballY + ballSpeedY * estimatedTime;

			return predictedY;
		}

		


	// TOURNOI

    // Fonction pour dessiner la liste des matchs
    function drawMatches(matches) {
        // Définir les paramètres de dessin
        const startX = 20; // Position X de départ des cadres
        const startY = canvas.height * 3 / 8; // Position Y de départ des cadres
        const frameWidth = canvas.width / 3; // Largeur des cadres
        const frameHeight = canvas.height / 12; // Hauteur des cadres
        const verticalGap = canvas.height / 30; // Espacement vertical entre les cadres

        ctx.fillStyle = "#ffe6b3"; // Couleur du texte en blanc
        ctx.font = "900 14px Noto Sans";

        // Dessiner chaque match dans un cadre différent
        matches.forEach((match, index) => {
            // Calculer les coordonnées du cadre pour ce match
            const frameX = startX;
            const frameY = startY + (frameHeight + verticalGap) * index;
            const textplayeroneMetrics = ctx.measureText(match.player1);
            const textplayertwoMetrics = ctx.measureText(match.player2);
            const textvsMetrics = ctx.measureText("vs");
            const textplayeroneWidth = textplayeroneMetrics.width;
            const textplayertwoWidth = textplayertwoMetrics.width;
            const textvsWidth = textvsMetrics.width;

            // Dessiner le cadre
            ctx.fillStyle = index % 2 === 0 ? "#0404ce" : "#f00"; // Alternance de couleurs
            ctx.fillRect(frameX, frameY, frameWidth, frameHeight);
            ctx.fillStyle = "#000";

            // Dessiner le texte du match
            ctx.fillText("Match " + (index + 1), frameX + 5, frameY + canvas.height / 30);
            if (match.winner != null) {
                if (match.player1 === match.winner )
                    ctx.fillText("winner : " + match.player1, frameX + frameWidth / 2, frameY + canvas.height / 30);
                else
                    ctx.fillText("winner : " + match.player2, frameX + frameWidth / 2, frameY + canvas.height / 30);
            }
            ctx.fillStyle = "#ffe6b3"; // Couleur du texte en blanc
            ctx.font = "900 14px Noto Sans";
            ctx.fillText("vs", (canvas.width / 3 - textvsWidth / 2) / 2 + frameX, frameY + 40);
            ctx.fillText(match.player1, canvas.width / 3 / 4 - textplayeroneWidth / 2 + frameX, frameY + 40);
            ctx.fillText(match.player2, (canvas.width / 3 - textplayertwoWidth / 2) * 3 / 4 + frameX, frameY + 40);
        });
    }

    function startTournament(participants) {
        endtournament = false;
        // Mélanger les participants
        shuffleArray(participants);
        // Créer les matchs
        createMatches(participants);
        drawtournament();
    }

    function matchesquarterended() {
        for (let i = 0; i < matchesquarter.length; i += 2) {
            let match = {player1: matchesquarter[i].winner, player2: matchesquarter[i + 1].winner, winner: null};
            matchessemi.push(match);
        }
        quarterfinal = 0;
        semifinal = 1;
        drawtournament();
    }

    function matchessemiended() {
        let match = {player1: matchessemi[0].winner, player2: matchessemi[1].winner, winner: null};
        matchesfinal.push(match);
        semifinal = 0;
        final = 1;
        drawtournament();
    }

    function matchesfinalended() {
        clearCanvas();
        ctx.fillStyle = "#000";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(pongImage, canvas.width * 1 / 6, canvas.height * 1 / 3, canvas.width * 2 / 3, canvas.height * 2 / 3);

        const text = "Winner is...";
        ctx.font = "900 40px Noto Sans";
        const textMetrics = ctx.measureText(text);
        const textWidth = textMetrics.width;


        // Ajuste la hauteur du texte en utilisant l'ascender et le descender
        const ascent = textMetrics.actualBoundingBoxAscent; // Ascender
        const descent = textMetrics.actualBoundingBoxDescent; // Descender

        // Dessiner le texte du menu
        ctx.fillStyle = "#ffe6b3";
        ctx.fillText(text, (canvas.width - textWidth) / 2, (canvas.height + ascent - descent) / 6);
        ctx.fillText(lastwinner + " !", canvas.width / 2, canvas.height * 1 / 4);
		hide_game_menu();
		draw_game_menu();
    }

    function cleartournament() {
        selectedMode = null;  // Variable pour suivre le mode de jeu sélectionné
        quarterfinal = 0;
        semifinal = 0;
        final = 0;
		endtournament = false;
		matchesquarter = [];
        matchessemi = [];
        matchesfinal = [];
		lastwinner = null;
		get_player_name().then(user => {
			playerOneName = user;
		}).catch(error => {
			console.error("Whats the duck ? who is who ? i'm a flying hamster !!!")
		});
		playerTwoName = canvas.dataset.playerTwo || "Player Two";
        score1 = 0;
        score2 = 0;
        lastscore = {score1: 0, score2: 0};
        predict = 0;
    }

    function drawtournament() {
        // Efface le canvas
        clearCanvas();
        ctx.fillStyle = "#a791e7";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(pongImage, 0, 0, canvas.width, canvas.height);

        const text = "Tournament";
        ctx.font = "900 80px Noto Sans";
        const textMetrics = ctx.measureText(text);
        const textWidth = textMetrics.width;

        // Ajuste la hauteur du texte en utilisant l'ascender et le descender
        const fontHeight = ctx.measureText('M').width; // Hauteur totale de la police
        const ascent = textMetrics.actualBoundingBoxAscent; // Ascender
        const descent = textMetrics.actualBoundingBoxDescent; // Descender
        const textHeight = ascent + descent;

        // Dessiner le texte du menu
        ctx.fillStyle = "#ffe6b3";
        ctx.fillText(text, (canvas.width - textWidth) / 2, (canvas.height + ascent - descent) / 6);
        // Dessiner les matchs
		hide_game_menu();
		draw_tournament_menu();
        if (quarterfinal == 1) {
            ctx.fillStyle = "#0404ce"; // Couleur bleue pour les boutons
            ctx.fillRect(20, canvas.height * 7 / 8 - 20, 260, 50);
            ctx.font = "900 30px Noto Sans";
            ctx.fillStyle = "#ffe6b3";
            ctx.fillText("Quarter-finals", 40, canvas.height * 7 / 8 + 15);
            drawMatches(matchesquarter);
            for (let i = 0; i <= matchesquarter.length; i++) {
                if (i == matchesquarter.length) {
                    matchesquarterended();
                    return;
                }
                if (matchesquarter[i].winner === null) {
                    if (matchesquarter[i].player1 === "exempt" || matchesquarter[i].player2 === "exempt") {
                        if (matchesquarter[i].player1 === "exempt")
                            matchesquarter[i].winner = matchesquarter[i].player2;
                        else
                            matchesquarter[i].winner = matchesquarter[i].player1;
                    }
                    else {
                        playerOneName = matchesquarter[i].player1;
                        playerTwoName = matchesquarter[i].player2;
                        break;
                    }
                }
            }
        }
        else if (semifinal == 1) {
            ctx.fillStyle = "#0404ce"; // Couleur bleue pour les boutons
            ctx.fillRect(20, canvas.height * 7 / 8 - 20, 210, 50);
            ctx.font = "900 30px Noto Sans";
            ctx.fillStyle = "#ffe6b3";
            ctx.fillText("Semi-finals", 40, canvas.height * 7 / 8 + 15);
            drawMatches(matchessemi);
            for (let i = 0; i <= matchessemi.length; i++) {
                if (i == matchessemi.length) {
                    matchessemiended();
                    return;
                }
                if (matchessemi[i].winner === null) {
                    if (matchessemi[i].player1 === "exempt" || matchessemi[i].player2 === "exempt") {
                        if (matchessemi[i].player1 === "exempt")
                            matchessemi[i].winner = matchessemi[i].player2;
                        else
                            matchessemi[i].winner = matchessemi[i].player1;
                    }
                    else {
                        playerOneName = matchessemi[i].player1;
                        playerTwoName = matchessemi[i].player2;
                        break;
                    }
                }

            }
        }
        else if (final == 1) {
            ctx.fillStyle = "#0404ce"; // Couleur bleue pour les boutons
            ctx.fillRect(20, canvas.height * 7 / 8 - 20, 210, 50);
            ctx.font = "900 30px Noto Sans";
            ctx.fillStyle = "#ffe6b3";
            ctx.fillText("Final", 80, canvas.height * 7 / 8 + 15);
            drawMatches(matchesfinal);
            playerOneName = matchesfinal[0].player1;
            playerTwoName = matchesfinal[0].player2;
        }
		// endgame = 0;
    }

    function updatetournament() {
        if (quarterfinal == 1) {
            for (let i = 0; i < matchesquarter.length; i++) {
                if (matchesquarter[i].winner === null) {
                    matchesquarter[i].winner = lastwinner;
                    break;
                }
            }
        }
        else if (semifinal == 1) {
            for (let i = 0; i < matchessemi.length; i++) {
                if (matchessemi[i].winner === null) {
                    matchessemi[i].winner = lastwinner;
                    break;
                }
            }
        }
        else if (final == 1) {
            if (matchesfinal[0].winner === null) {
                matchesfinal[0].winner = lastwinner;
                endtournament = true;
            }
        }
    }

    // Fonction pour mélanger un tableau
    function shuffleArray(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
        return array;
    }

    // Fonction pour créer les matchs
    function createMatches(participants) {

        const numParticipants = participants.length;
        if (numParticipants > 4) {
            // Créer les paires de matchs en associant chaque participant à un autre
            for (let i = 0; i < numParticipants; i += 2) {
                let match = {player1: participants[i], player2: participants[i + 1], winner: null};
                matchesquarter.push(match);
            }
        }
        else {
            // Créer les paires de matchs en associant chaque participant à un autre
            for (let i = 0; i < numParticipants; i += 2) {
                let match = {player1: participants[i], player2: participants[i + 1], winner: null};
                matchessemi.push(match);
            }
        }
    }
	hide_game_menu();
	draw_game_menu();
	resetGame();
	drawDragonBackground();
	initBricks();
    AIEverySecond();
    AIEverymilliSecond();
	document.addEventListener("keydown", handleKeydown);
	document.addEventListener("keyup", handleKeyup);
});
