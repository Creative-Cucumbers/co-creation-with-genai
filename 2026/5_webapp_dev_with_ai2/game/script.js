// script.js
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

// Set canvas size
canvas.width = 800;
canvas.height = 600;

// Player object
const player = {
  x: canvas.width / 2,
  y: canvas.height - 50,
  width: 50,
  height: 50,
  color: "blue",
  speed: 5,
};

// Bullets array
const bullets = [];

// Enemies array
const enemies = [];

let score = 0;
let gameover = false;
let timeLeft = 15;

// Draw player
function drawPlayer() {
  ctx.fillStyle = player.color;
  ctx.fillRect(player.x, player.y, player.width, player.height);
}

// Draw bullets
function drawBullets() {
  ctx.fillStyle = "white";
  bullets.forEach((bullet) => {
    ctx.fillRect(bullet.x, bullet.y, 5, 10);
  });
}

// Draw enemies
function drawEnemies() {
  ctx.fillStyle = "red";
  enemies.forEach((enemy) => {
    ctx.fillRect(enemy.x, enemy.y, enemy.width, enemy.height);
  });
}

// Update player position
function updatePlayer() {
  if (keys.ArrowLeft && player.x > 0) {
    player.x -= player.speed;
  }
  if (keys.ArrowRight && player.x < canvas.width - player.width) {
    player.x += player.speed;
  }
}

// Update bullets position
function updateBullets() {
  bullets.forEach((bullet) => {
    bullet.y -= 5;
  });
}

function updateEnemies() {
  if (Math.random() < 0.01) {
    // 1%の確率で敵を生成
    const enemy = {
      x: Math.random() * (canvas.width - 50),
      y: 0,
      width: 50,
      height: 50,
    };
    enemies.push(enemy);
  }

  enemies.forEach((enemy) => {
    enemy.y += 2;
    if (enemy.y > canvas.height) {
      enemies.splice(enemies.indexOf(enemy), 1);
    }
  });
}

// Check collision between bullets and enemies
function checkCollision() {
  bullets.forEach((bullet, bulletIndex) => {
    enemies.forEach((enemy, enemyIndex) => {
      if (
        bullet.x < enemy.x + enemy.width &&
        bullet.x + 5 > enemy.x &&
        bullet.y < enemy.y + enemy.height &&
        bullet.y + 10 > enemy.y
      ) {
        bullets.splice(bulletIndex, 1);
        enemies.splice(enemyIndex, 1);
        score += 10;
      }
    });
  });
}

// Check collision between player and enemies
function checkPlayerCollision() {
  enemies.forEach((enemy) => {
    if (
      player.x < enemy.x + enemy.width &&
      player.x + player.width > enemy.x &&
      player.y < enemy.y + enemy.height &&
      player.y + player.height > enemy.y
    ) {
      gameover = true;
    }
  });
}

// Draw score
function drawScore() {
  ctx.fillStyle = "white";
  ctx.font = "20px Arial";
  ctx.fillText("Score: " + score, 10, 30);
}

// Draw time left
function drawTimeLeft() {
  ctx.fillStyle = "white";
  ctx.font = "20px Arial";
  ctx.fillText("Time Left: " + timeLeft, canvas.width - 150, 30);
}

// Game loop
function gameLoop() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  updatePlayer();
  updateBullets();
  updateEnemies();
  checkCollision();
  checkPlayerCollision();
  drawPlayer();
  drawBullets();
  drawEnemies();
  drawScore();
  drawTimeLeft();

  if (!gameover) {
    if (timeLeft > 0) {
      timeLeft -= 1 / 60;
    } else {
      gameover = true;
    }
    requestAnimationFrame(gameLoop);
  } else {
    ctx.fillStyle = "white";
    ctx.font = "40px Arial";
    ctx.fillText("Game Over", canvas.width / 2 - 100, canvas.height / 2);
    ctx.fillText(
      "Score: " + score,
      canvas.width / 2 - 60,
      canvas.height / 2 + 50
    );
  }
}

// Keyboard input handling
const keys = {};
window.addEventListener("keydown", (event) => {
  keys[event.key] = true;
  if (event.key === " ") {
    bullets.push({
      x: player.x + player.width / 2,
      y: player.y,
    });
  }
});
window.addEventListener("keyup", (event) => {
  keys[event.key] = false;
});

// Start the game loop
gameLoop();
