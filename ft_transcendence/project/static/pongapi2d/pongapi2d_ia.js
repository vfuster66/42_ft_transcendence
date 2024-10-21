(function() {
    // Global Variables
    var DIRECTION = {
        IDLE: 0,
        UP: 1,
        DOWN: 2,
        LEFT: 3,
        RIGHT: 4
    };

    var rounds = [5];
    var colors = ['#1abc9c', '#2ecc71', '#3498db', '#e74c3c', '#9b59b6'];
    var beep1 = new Audio("https://commondatastorage.googleapis.com/codeskulptor-assets/Collision8-Bit.ogg");
    var beep2 = new Audio("https://codeskulptor-demos.commondatastorage.googleapis.com/GalaxyInvaders/pause.wav");
    var beep3 = new Audio("https://commondatastorage.googleapis.com/codeskulptor-demos/pyman_assets/theygotcha.ogg");

    // The ball object (The cube that bounces back and forth)
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
                height: 100,
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

            this.player = Paddle.new.call(this, 'left');
            this.paddle = Paddle.new.call(this, 'right');
            this.ball = Ball.new.call(this);

            this.paddle.speed = 8;
            this.running = this.over = false;
            this.turn = this.paddle;
            this.timer = this.round = 0;
            this.color = 'black';

            Pong.menu();
            Pong.listen();
        },

        endMatch: function (winner) {
            let player1Score = this.player.score;
            let aiScore = this.paddle.score;
            let winnerName = winner === 'player' ? 'Player 1' : 'AI';

            // Envoyer les scores et le nom du gagnant au serveur
            fetch('/api/end_match/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    winner: winnerName,
                    player1_score: player1Score,
                    ai_score: aiScore
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok ' + response.statusText);
                }
                return response.json();
            })
            .then(data => {
                console.log('Match result sent to server:', data);
            })
            .catch(error => console.error('Error sending match result:', error));

            let url = winner === 'player' ? '/pongapi2d_success/' : '/pongapi2d_failure/';
            window.location.href = `${url}?player1Score=${player1Score}&aiScore=${aiScore}`;
        },

        menu: function () {
            Pong.draw();
            this.context.font = '50px Courier New';
            this.context.fillStyle = this.color;
            this.context.fillRect(this.canvas.width / 2 - 350, this.canvas.height / 2 - 48, 700, 100);
            this.context.fillStyle = '#ffffff';
            this.context.fillText('Press any key to begin', this.canvas.width / 2, this.canvas.height / 2 + 15);
        },

        update: function () {
            if (!this.over) {
                if (this.ball.x <= 0) Pong._resetTurn.call(this, this.paddle, this.player);
                if (this.ball.x >= this.canvas.width - this.ball.width) Pong._resetTurn.call(this, this.player, this.paddle);
                if (this.ball.y <= 0) this.ball.moveY = DIRECTION.DOWN;
                if (this.ball.y >= this.canvas.height - this.ball.height) this.ball.moveY = DIRECTION.UP;

                if (this.player.move === DIRECTION.UP) this.player.y -= this.player.speed;
                else if (this.player.move === DIRECTION.DOWN) this.player.y += this.player.speed;

                if (Pong._turnDelayIsOver.call(this) && this.turn) {
                    this.ball.moveX = this.turn === this.player ? DIRECTION.LEFT : DIRECTION.RIGHT;
                    this.ball.moveY = [DIRECTION.UP, DIRECTION.DOWN][Math.round(Math.random())];
                    this.ball.y = Math.floor(Math.random() * (this.canvas.height - 200)) + 100;
                    this.turn = null;
                }

                if (this.player.y <= 0) this.player.y = 0;
                else if (this.player.y >= (this.canvas.height - this.player.height)) this.player.y = (this.canvas.height - this.player.height);

                if (this.ball.moveY === DIRECTION.UP) this.ball.y -= (this.ball.speed / 1.5);
                else if (this.ball.moveY === DIRECTION.DOWN) this.ball.y += (this.ball.speed / 1.5);
                if (this.ball.moveX === DIRECTION.LEFT) this.ball.x -= this.ball.speed;
                else if (this.ball.moveX === DIRECTION.RIGHT) this.ball.x += this.ball.speed;

                if (this.paddle.move === DIRECTION.UP) this.paddle.y -= this.paddle.speed;
                else if (this.paddle.move === DIRECTION.DOWN) this.paddle.y += this.paddle.speed;

                if (this.paddle.y <= 0) this.paddle.y = 0;
                else if (this.paddle.y >= (this.canvas.height - this.paddle.height)) this.paddle.y = (this.canvas.height - this.paddle.height);

                if (this.ball.x - this.ball.width <= this.player.x && this.ball.x >= this.player.x - this.player.width) {
                    if (this.ball.y <= this.player.y + this.player.height && this.ball.y + this.ball.height >= this.player.y) {
                        this.ball.x = (this.player.x + this.ball.width);
                        this.ball.moveX = DIRECTION.RIGHT;
                    }
                }

                if (this.ball.x - this.ball.width <= this.paddle.x && this.ball.x >= this.paddle.x - this.paddle.width) {
                    if (this.ball.y <= this.paddle.y + this.paddle.height && this.ball.y + this.ball.height >= this.paddle.y) {
                        this.ball.x = (this.paddle.x - this.ball.width);
                        this.ball.moveX = DIRECTION.LEFT;
                    }
                }
            }

            if (this.player.score === rounds[this.round]) {
                if (!rounds[this.round + 1]) {
                    this.over = true;
                    setTimeout(function () { Pong.endMatch('player'); }, 1000);
                } else {
                    this.color = this._generateRoundColor();
                    this.player.score = this.paddle.score = 0;
                    this.player.speed += 0.5;
                    this.paddle.speed += 1;
                    this.ball.speed += 1;
                    this.round += 1;
                }
            }
            else if (this.paddle.score === rounds[this.round]) {
                this.over = true;
                setTimeout(function () { Pong.endMatch('ai'); }, 1000);
            }
        },

        draw: function () {
            this.context.clearRect(0, 0, this.canvas.width, this.canvas.height);
            this.context.fillStyle = this.color;
            this.context.fillRect(0, 0, this.canvas.width, this.canvas.height);
            this.context.fillStyle = '#ffffff';
            this.context.fillRect(this.player.x, this.player.y, this.player.width, this.player.height);
            this.context.fillRect(this.paddle.x, this.paddle.y, this.paddle.width, this.paddle.height);
            if (Pong._turnDelayIsOver.call(this)) {
                this.context.fillRect(this.ball.x, this.ball.y, this.ball.width, this.ball.height);
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
            this.context.fillText(this.player.score.toString(), (this.canvas.width / 2) - 300, 200);
            this.context.fillText(this.paddle.score.toString(), (this.canvas.width / 2) + 300, 200);
            this.context.font = '30px Courier New';
            this.context.fillText('Round ' + (Pong.round + 1), (this.canvas.width / 2), 35);
            this.context.font = '40px Courier';
            this.context.fillText(rounds[Pong.round] ? rounds[Pong.round] : rounds[Pong.round - 1], (this.canvas.width / 2), 100);
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
                    Pong.initAI();
                }
                if (key.code === 'KeyW') Pong.player.move = DIRECTION.UP;
                if (key.code === 'KeyS') Pong.player.move = DIRECTION.DOWN;
            });

            document.addEventListener('keyup', function (key) {
                if (key.code === 'KeyW' || key.code === 'KeyS') Pong.player.move = DIRECTION.IDLE;
            });
        },

        _resetTurn: function (victor, loser) {
            this.ball = Ball.new.call(this, this.ball.speed);
            this.turn = loser;
            this.timer = (new Date()).getTime();
            victor.score++;
        },

        _turnDelayIsOver: function () {
            return ((new Date()).getTime() - this.timer >= 1000);
        },

        _generateRoundColor: function () {
            var newColor = colors[Math.floor(Math.random() * colors.length)];
            if (newColor === this.color) return Pong._generateRoundColor();
            return newColor;
        },

        predictBallYPosition: function(ball, targetX) {
            let ballCopy = { ...ball };
            let direction = ball.moveY === DIRECTION.UP ? -1 : 1;
        
            while (ballCopy.x > targetX) {
                ballCopy.x -= ballCopy.speed;
                ballCopy.y += direction * (ballCopy.speed / 1.5);
        
                if (ballCopy.y <= 0) {
                    ballCopy.y = -ballCopy.y;
                    direction = 1;
                } else if (ballCopy.y >= Pong.canvas.height - ballCopy.height) {
                    ballCopy.y = 2 * (Pong.canvas.height - ballCopy.height) - ballCopy.y;
                    direction = -1;
                }
            }
        
            return ballCopy.y;
        },
        
        initAI: function () {
            setInterval(function () {
                let predictedY = Pong.predictBallYPosition(Pong.ball, Pong.paddle.x);
                if (predictedY < Pong.paddle.y + Pong.paddle.height / 2) {
                    Pong.paddle.move = DIRECTION.UP;
                } else if (predictedY > Pong.paddle.y + Pong.paddle.height / 2) {
                    Pong.paddle.move = DIRECTION.DOWN;
                } else {
                    Pong.paddle.move = DIRECTION.IDLE;
                }
            }, 1000 / 60); // Update every frame
        }        
    };

    var Pong = Object.assign({}, Game);

    function getCSRFToken() {
        const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
        return csrfToken;
    }

    const csrftoken = getCSRFToken();
    console.log(`CSRF Token: ${csrftoken}`);

    function getJWTToken() {
        const token = localStorage.getItem('jwtToken');
        console.log(`Retrieved JWT token from localStorage: ${token}`);
        return token;
    }

    function setJWTToken(token) {
        localStorage.setItem('jwtToken', token);
        console.log(`Stored JWT token in localStorage: ${token}`);
    }

    // Function to login and obtain JWT token
    function login(username, password) {
        console.log(`Logging in with username: ${username}`);
        fetch('/api/token/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify({ username: username, password: password })
        })
        .then(response => response.json())
        .then(data => {
            if (data.access) {
                setJWTToken(data.access);
                console.log('JWT Token obtained and stored');
            } else {
                console.error('Login failed:', data);
            }
        })
        .catch(error => {
            console.error('Error during login:', error);
        });
    }

    function updateGame() {
        console.log('Calling updateGame');
        const token = getJWTToken();
        console.log(`JWT Token: ${token}`);
        fetch('/api/games/1/move_ball/', { 
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
                'X-CSRFToken': csrftoken
            }
        })
        .then(response => {
            console.log('Response from API received');
            if (!response.ok) {
                console.log('Network response was not ok');
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            console.log('Data from API:', data);
            Pong.ball.x = data.ball_position_x * (Pong.canvas.width / 100);
            Pong.ball.y = data.ball_position_y * (Pong.canvas.height / 100);
            Pong.draw();
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
    }

    function movePaddle(paddle, dy) {
        paddle.y += dy;
        const token = getJWTToken();
        fetch(`/api/games/1/move_paddle/`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
                'X-CSRFToken': csrftoken 
            },
            body: JSON.stringify({ position: paddle.y * (100 / Pong.canvas.height) })
        });
    }

    document.addEventListener('keydown', function(event) {
        if (event.key === 'ArrowUp') {
            movePaddle(Pong.paddle, -10);
        } else if (event.key === 'ArrowDown') {
            movePaddle(Pong.paddle, 10);
        } else if (event.key === 'w') {
            movePaddle(Pong.player, -10);
        } else if (event.key === 's') {
            movePaddle(Pong.player, 10);
        }
    });

    document.addEventListener('keyup', function(event) {
        if (event.key === 'ArrowUp' || event.key === 'ArrowDown') {
            Pong.paddle.dy = 0;
        } else if (event.key === 'w' || event.key === 's') {
            Pong.player.dy = 0;
        }
    });

    Pong.initialize();
    setInterval(updateGame, 1000 / 60); // 60 FPS

    // Utilisation des variables d'environnement injectées depuis le template
    var user = POSTGRES_USER;
    var password = POSTGRES_PASSWORD;

    // Exemple d'appel de la fonction de connexion avec les variables d'environnement
    login(user, password);
})();



