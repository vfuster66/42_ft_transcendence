const Game = require('./game');

const GameView = function(ctx, canvasSize)
{
	this.ctx = ctx;
	this.canvasSize = canvasSize;
	this.game = new Game({
		canvasSize: this.canvasSize,
		ctx: this.ctx,
		gameView: this
	});
	this.defender = this.game.defender;
	this.isPaused = false;

	this.rightPressed = false;
	this.leftPressed = false;
	this.spacePressed = false;



	this.addKeyListeners();
};

GameView.prototype.toggleAudio = function()
{

};

GameView.prototype.start = function()
{
	this.interval = setInterval(() =>
	{
		if (!this.isPaused)
		{
			this.game.draw(this.ctx);
			this.addLivesText(this.ctx);
			this.addScoreText(this.ctx);
			this.addLevelText(this.ctx);
			this.moveDefender();
			this.game.moveInvaders();
			this.game.addUfo();
			this.game.step();
		}
	}, 10);

	this.toggle = setInterval(() =>
	{
		if (!this.isPaused) this.game.toggleInvaders();
	}, 500);
};

GameView.prototype.stop = function()
{
	clearInterval(this.interval);
	clearInterval(this.toggle);

	this.interval     = null;
	this.toggle       = null;
	this.rightPressed = false;
	this.leftPressed  = false;
	this.spacePressed = false;
	this.isPaused     = false;
	this.defender     = this.game.defender;

	this.game = new Game({
		canvasSize: this.canvasSize,
		gameView:   this,
		ctx:        this.ctx
	});
};

GameView.prototype.restart = function()
{
	this.stop();
	this.start();
};

GameView.prototype.welcome = function()
{
	this.ctx.fillStyle = '#000';
	this.ctx.fillRect(0, 0, this.game.DIM_X, this.game.DIM_Y);
};

GameView.prototype.pause = function()
{
	this.isPaused = true;
};

GameView.prototype.resume = function()
{
	this.isPaused = false;
};

GameView.prototype.gameOver = function () {
	const finalScore = this.game.score;
	
	this.stop();
	
	if (window.isTournamentMode === 'true') {
		console.log('Tournament mode enabled. Tournament ID:', window.tournamentId);
	
		fetch('/invaders_match_end/', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify({
			match_id: window.matchId,
			score: finalScore,
		}),
		})
		.then(response => {
		if (!response.ok) {
			throw new Error('Network response was not ok ' + response.statusText);
		}
		return response.json();
		})
		.then(data => {
		if (data.status === 'success') {
			if (window.tournamentId) {
			const redirectUrl = `/invaders_tournament_details/${window.tournamentId}/`;
			console.log('Redirecting to:', redirectUrl);
			window.location.href = redirectUrl;
			} else {
			console.error('Tournament ID is not defined.');
			}
		} else {
			console.error('Error:', data.message);
		}
		})
		.catch(error => console.error('Error sending match result:', error));
	} else {
		const urlParams = new URLSearchParams({
		score: finalScore,
		lives: this.game.defenderLives
		});
	
		const redirectUrl = `/invaders_lose/?${urlParams.toString()}`;
		window.location.href = redirectUrl;
	}
};



GameView.KEY_BINDS =
{
	'left': [-2, 0],
	'right': [2, 0]
};

GameView.prototype.addLivesText = function(ctx)
{
	let x = this.game.DIM_X * .87, y = this.game.DIM_Y * .05;

	ctx.font = "23px Bungee Inline";
	ctx.fillText(`LIVES: ${this.game.defenderLives}`, x, y);
};

GameView.prototype.addMenu = function(ctx)
{
	let x = this.game.DIM_X * .5, y = this.game.DIM_Y * .1;
};

GameView.prototype.addScoreText = function (ctx) {
    let x = this.game.DIM_X * .01, y = this.game.DIM_Y * .05;
    ctx.fillText(`SCORE: ${this.game.score}`, x, y);
};


GameView.prototype.addLevelText = function(ctx)
{
	let x = this.game.DIM_X * .01, y = this.game.DIM_Y * .95;
	ctx.fillText(`LEVEL: ${this.game.level}`, x, y);
}

GameView.prototype.bindKeyHandlers = function()
{
	const defender = this.defender;

	Object.keys(GameView.KEY_BINDS).forEach(k =>
	{
		let offset = GameView.KEY_BINDS[k];
		key(k, function() { defender.power(offset); });
	});

	key('space', function() { defender.fireBullet(); });
};

GameView.prototype.addKeyListeners = function()
{
	document.addEventListener('keydown', this.handleKeyDown.bind(this), false);
	document.addEventListener('keyup', this.handleKeyUp.bind(this), false);
};

GameView.prototype.handleKeyDown = function(e)
{
	if (e.keyCode === 37)
	{
		this.leftPressed = true;
	}
	else if (e.keyCode === 39)
	{
		this.rightPressed = true;
	}

	if (e.keyCode === 32)
	{
		this.spacePressed = true;
	}
};

GameView.prototype.handleKeyUp = function(e)
{
	if (e.keyCode === 37)
	{
		this.leftPressed = false;
	}
	else if (e.keyCode === 39)
	{
		this.rightPressed = false;
	}

	if (e.keyCode === 32)
	{
		this.spacePressed = false;
	}
};

GameView.prototype.moveDefender = function()
{
	if (this.leftPressed)
	{
		this.defender.power([-3,0]);
	}
	else if (this.rightPressed)
	{
		this.defender.power([3,0]);
	}

	if (this.spacePressed)
	{
		this.defender.fireBullet();
	}
};

module.exports = GameView;
