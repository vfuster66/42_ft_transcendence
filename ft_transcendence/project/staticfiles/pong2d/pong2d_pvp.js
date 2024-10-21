var DIRECTION = {
    IDLE: 0,
    UP: 1,
    DOWN: 2,
    LEFT: 3,
    RIGHT: 4
};

var rounds = [5, 5, 3, 3, 2];
var colors = ['#1abc9c', '#2ecc71', '#3498db', '#e74c3c', '#9b59b6'];
var beep1 = new Audio("https://commondatastorage.googleapis.com/codeskulptor-assets/Collision8-Bit.ogg");
var beep2 = new Audio("https://codeskulptor-demos.commondatastorage.googleapis.com/GalaxyInvaders/pause.wav");
var beep3 = new Audio("https://commondatastorage.googleapis.com/codeskulptor-demos/pyman_assets/theygotcha.ogg");

var Ball = {
    new: function (incrementedSpeed) {
        return {
            width: 18,
            height: 18,
            x: (this.canvas.width / 2) - 9,
            y: (this.canvas.height / 2) - 9,
            moveX: DIRECTION.IDLE,
            moveY: DIRECTION.IDLE,
            speed: incrementedSpeed || 9
        };
    }
};

var Paddle = {
    new: function (side) {
        return {
            width: 18,
            height: 90,
            x: side === 'left' ? 150 : this.canvas.width - 150,
            y: (this.canvas.height / 2) - 35,
            score: 0,
            move: DIRECTION.IDLE,
            speed: 10
        };
    }
};

var Game = {
    initialize: function () {
        this.canvas = document.querySelector('canvas');
        this.context = this.canvas.getContext('2d');

        this.canvas.width = 1400;
        this.canvas.height = 1000;

        this.canvas.style.width = (this.canvas.width / 2) + 'px';
        this.canvas.style.height = (this.canvas.height / 2) + 'px';

        this.player1 = Paddle.new.call(this, 'left');
        this.player2 = Paddle.new.call(this, 'right');
        this.ball = Ball.new.call(this);

        this.player2.speed = 8;
        this.running = this.over = false;
        this.turn = this.player2;
        this.timer = this.round = 0;
        this.color = 'black';

        Pong.menu();
        Pong.listen();
    },

    endMatch: function (winner) {
        let player1Score = this.player1.score;
        let player2Score = this.player2.score;
        let winnerId = (winner === 'player1') ? window.player1Id : window.player2Id;

        if (!winnerId || !window.matchId) {
            console.error('Missing winnerId or matchId');
            return;
        }

        const requestData = {
            winner: winnerId,
            match_id: window.matchId,
            player1_score: player1Score,
            player2_score: player2Score
        };

        fetch('/pong2d_match_end/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                console.log('Match result sent to application:', data);
                window.location.href = `/pong2d_pvp_success/${window.tournamentId}`;
            } else {
                console.error('Error:', data.message);
            }
        })
        .catch(error => console.error('Error sending match result:', error));
    },

    menu: function () {
        Pong.draw();

        this.context.font = '50px Courier New';
        this.context.fillStyle = this.color;

        this.context.fillRect(
            this.canvas.width / 2 - 350,
            this.canvas.height / 2 - 48,
            700,
            100
        );

        this.context.fillStyle = '#ffffff';

        this.context.fillText('Press any key to begin',
            this.canvas.width / 2,
            this.canvas.height / 2 + 15
        );
    },

    update: function () {
        if (!this.over) {
            if (this.ball.x <= 0) Pong._resetTurn.call(this, this.player2, this.player1);
            if (this.ball.x >= this.canvas.width - this.ball.width) Pong._resetTurn.call(this, this.player1, this.player2);
            if (this.ball.y <= 0) this.ball.moveY = DIRECTION.DOWN;
            if (this.ball.y >= this.canvas.height - this.ball.height) this.ball.moveY = DIRECTION.UP;
    
            if (this.player1.move === DIRECTION.UP) this.player1.y -= this.player1.speed;
            else if (this.player1.move === DIRECTION.DOWN) this.player1.y += this.player1.speed;
    
            if (this.player2.move === DIRECTION.UP) this.player2.y -= this.player2.speed;
            else if (this.player2.move === DIRECTION.DOWN) this.player2.y += this.player2.speed;
    
            if (Pong._turnDelayIsOver.call(this) && this.turn) {
                this.ball.moveX = this.turn === this.player1 ? DIRECTION.LEFT : DIRECTION.RIGHT;
    
                // Utiliser des angles moins importants pour le mouvement Y
                const angle = Math.random() < 0.5 ? DIRECTION.UP : DIRECTION.DOWN;
                this.ball.moveY = angle;
    
                this.ball.y = this.canvas.height / 2;
                this.turn = null;
            }
    
            if (this.player1.y <= 0) this.player1.y = 0;
            else if (this.player1.y >= (this.canvas.height - this.player1.height)) this.player1.y = (this.canvas.height - this.player1.height);
    
            if (this.player2.y <= 0) this.player2.y = 0;
            else if (this.player2.y >= (this.canvas.height - this.player2.height)) this.player2.y = (this.canvas.height - this.player2.height);
    
            if (this.ball.moveY === DIRECTION.UP) this.ball.y -= (this.ball.speed / 1.5);
            else if (this.ball.moveY === DIRECTION.DOWN) this.ball.y += (this.ball.speed / 1.5);
            if (this.ball.moveX === DIRECTION.LEFT) this.ball.x -= this.ball.speed;
            else if (this.ball.moveX === DIRECTION.RIGHT) this.ball.x += this.ball.speed;
    
            if (this.ball.x - this.ball.width <= this.player1.x && this.ball.x >= this.player1.x - this.player1.width) {
                if (this.ball.y <= this.player1.y + this.player1.height && this.ball.y + this.ball.height >= this.player1.y) {
                    this.ball.x = (this.player1.x + this.ball.width);
                    this.ball.moveX = DIRECTION.RIGHT;
    
                    beep1.play();
                }
            }
    
            if (this.ball.x - this.ball.width <= this.player2.x && this.ball.x >= this.player2.x - this.player2.width) {
                if (this.ball.y <= this.player2.y + this.player2.height && this.ball.y + this.ball.height >= this.player2.y) {
                    this.ball.x = (this.player2.x - this.ball.width);
                    this.ball.moveX = DIRECTION.LEFT;
    
                    beep1.play();
                }
            }
        }
    
        if (this.player1.score === 5) {
            this.over = true;
            setTimeout(() => this.endMatch('player1'), 1000);
        }
        else if (this.player2.score === 5) {
            this.over = true;
            setTimeout(() => this.endMatch('player2'), 1000);
        }
    },

    draw: function () {
        this.context.clearRect(
            0,
            0,
            this.canvas.width,
            this.canvas.height
        );

        this.context.fillStyle = this.color;

        this.context.fillRect(
            0,
            0,
            this.canvas.width,
            this.canvas.height
        );

        this.context.fillStyle = '#ffffff';

        this.context.fillRect(
            this.player1.x,
            this.player1.y,
            this.player1.width,
            this.player1.height
        );

        this.context.fillRect(
            this.player2.x,
            this.player2.y,
            this.player2.width,
            this.player2.height
        );

        if (Pong._turnDelayIsOver.call(this)) {
            this.context.fillRect(
                this.ball.x,
                this.ball.y,
                this.ball.width,
                this.ball.height
            );
        }

        this.context.beginPath();
        this.context.setLineDash([7, 15]);
        this.context.moveTo((this.canvas.width / 2), this.canvas.height - 140);
        this.context.lineTo((this.canvas.width / 2), 140);
        this.context.lineWidth = 10;
        this.context.strokeStyle = '#ffffff';
        this.context.stroke();

        this.context.font = '100px Courier New';
        this.context.textAlign = 'center';

        this.context.fillText(
            this.player1.score.toString(),
            (this.canvas.width / 2) - 300,
            200
        );

        this.context.fillText(
            this.player2.score.toString(),
            (this.canvas.width / 2) + 300,
            200
        );

        this.context.font = '30px Courier New';

        this.context.fillText(
            'First to 5 Wins!',
            (this.canvas.width / 2),
            35
        );
    },

    loop: function () {
        Pong.update();
        Pong.draw();

        if (!Pong.over) requestAnimationFrame(Pong.loop);
    },

    listen: function () {
        document.addEventListener('keydown', function (key) {
            if (Pong.running === false) {
                Pong.running = true;
                window.requestAnimationFrame(Pong.loop);
            }

            if (key.code === 'KeyW') Pong.player1.move = DIRECTION.UP;
            if (key.code === 'KeyS') Pong.player1.move = DIRECTION.DOWN;

            if (key.code === 'KeyI') Pong.player2.move = DIRECTION.UP;
            if (key.code === 'KeyK') Pong.player2.move = DIRECTION.DOWN;
        });

        document.addEventListener('keyup', function (key) {
            if (key.code === 'KeyW' || key.code === 'KeyS') {
                Pong.player1.move = DIRECTION.IDLE;
            }

            if (key.code === 'KeyI' || key.code === 'KeyK') {
                Pong.player2.move = DIRECTION.IDLE;
            }
        });
    },

    _resetTurn: function (victor, loser) {
        this.ball = Ball.new.call(this, this.ball.speed);
        this.turn = loser;
        this.timer = (new Date()).getTime();
    
        // Ajuster les directions initiales de la balle pour un angle moins important
        this.ball.moveX = victor === this.player1 ? DIRECTION.LEFT : DIRECTION.RIGHT;
        this.ball.moveY = [DIRECTION.UP, DIRECTION.DOWN][Math.floor(Math.random() * 2)];
    
        victor.score++;
        beep2.play();
    },
    
    _turnDelayIsOver: function () {
        return ((new Date()).getTime() - this.timer >= 1000);
    },

    _generateRoundColor: function () {
        var newColor = colors[Math.floor(Math.random() * colors.length)];
        if (newColor === this.color) return Pong._generateRoundColor();
        return newColor;
    }
};

var Pong = Object.assign({}, Game);
Pong.initialize();
