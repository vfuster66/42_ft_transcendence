const GameView = require('./game_view');

document.addEventListener('DOMContentLoaded', () =>
{
	const canvas = document.getElementById('game-canvas');
	canvas.height = 600;
	canvas.width = 900;

	const canvasSize = [canvas.width, canvas.height];
	const ctx = canvas.getContext('2d');
	const gameView = new GameView(ctx, canvasSize);

	gameView.welcome();

	const mainLogo = document.getElementById('main-logo');
	const playGameButton = document.getElementById('play-game');
	const gameOverImage = document.getElementById('game-over');

	const grunt = document.getElementById('grunt-1');
	const soldier = document.getElementById('soldier-1');
	const invader = document.getElementById('invader-1');
	const ufo = document.getElementById('ufo');
	const invaderInfo = document.getElementById('invader-info');
	const splashInstruction = document.getElementById('splash-instruction');

	playGameButton.addEventListener("click", () =>
	{
		playGameButton.className = 'hide';
		mainLogo.className = 'hide';
		gameOverImage.className = 'hide';
		grunt.className = 'hide';
		soldier.className = 'hide';
		invader.className = 'hide';
		ufo.className = 'hide';
		invaderInfo.className = 'hide';
		splashInstruction.className = 'hide';

		gameView.start();
	});
});
