// Because of Jinja syntax, "const pairs: string" and "const username: string"
// must have been assigned in game.html.
// <script type="text/javascript">
//   const pairs = "{{ pairs }}"
//   const username = "{{ username }}";
// </script>

const playGameScreen = document.querySelector(".play-game-container");
const gameCardContainer = document.querySelector(".game-cards-container");
const gameOverContainer = document.querySelector(".game-over-container");
const scoreOutput = document.getElementById("score_output");
const likeButtons = document.querySelectorAll(".photo-card__button");
let timeBonusBase = 10;

let gameState = {
  matchedPairs: 0,
  firstFlip: "",
  firstFlipId: "",
  secondFlip: "",
  secondFlipId: "",
  compering: false,
  consecutivePair: 0,
  score: 0,
};

const assignClassAccordingToPairs = (count) => {
  switch (count) {
    case "6":
      gameCardContainer.classList.add("pairs6");
      break;
    case "12":
      gameCardContainer.classList.add("pairs12");
      break;
    case "18":
      gameCardContainer.classList.add("pairs18");
      break;
    default:
      console.log("Wrong pairs number");
  }
};

const calculateTimeBonusBase = () => {
  const interval = setInterval(() => {
    if (timeBonusBase === 0) return clearInterval(interval);
    timeBonusBase--;
  }, 6000);
};

const flipCard = (card) => {
  if (!gameState.firstFlip) {
    gameState.firstFlip = card.firstElementChild.src;
    gameState.firstFlipId = card.id;
  } else {
    gameState.secondFlip = card.firstElementChild.src;
    gameState.secondFlipId = card.id;
  }
  card.classList.add("flipped");
};

const resetConsecutivePairs = () => {
  gameState = {
    ...gameState,
    consecutivePair: 0,
  };
};

const animateNoMatch = () => {
  const firstCard = document.getElementById(gameState.firstFlipId);
  const secondCard = document.getElementById(gameState.secondFlipId);
  firstCard.classList.add("no-match");
  secondCard.classList.add("no-match");
  // Return promise, so animaton can finish and user can't flip other cards
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      firstCard.classList.remove("no-match");
      secondCard.classList.remove("no-match");
      firstCard.classList.remove("flipped");
      secondCard.classList.remove("flipped");

      resolve();
    }, 500);
  });
};

const animateMatch = () => {
  const firstCard = document.getElementById(gameState.firstFlipId);
  const secondCard = document.getElementById(gameState.secondFlipId);
  firstCard.classList.add("match");
  secondCard.classList.add("match");
};

const handleScoreIncrement = () => {
  scoreOutput.classList.add("add-points");
  const timeBonus = Math.floor(50 * (timeBonusBase / 100));
  const consecutiveBonus = Math.floor(100 * 0.5 * gameState.consecutivePair);
  const currentScore = gameState.score + 100 + consecutiveBonus + timeBonus;
  gameState = {
    ...gameState,
    score: currentScore,
    consecutivePair: gameState.consecutivePair++,
  };

  setTimeout(() => {
    scoreOutput.innerText = currentScore;
  }, 250);
  setTimeout(() => {
    scoreOutput.classList.remove("add-points");
  }, 500);
};

const recordUserScore = async () => {
  if (username === "Stranger") return;
  const data = {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ score: gameState.score, username }),
  };

  try {
    await fetch("/getscores", data);
  } catch (err) {
    console.log(err);
  }
};

const showFinalScore = () => {
  document.getElementById("final_score").innerText = gameState.score;
};

const hidePlayGameScreen = () => {
  // Animate cards
  [...gameCardContainer.children].forEach((card) => {
    card.classList.remove("match");
    card.classList.add("game-over");
    setTimeout(() => {
      const direction1 = Math.random() > 0.5 ? 1 : -1;
      const direction2 = Math.random() > 0.5 ? 1 : -1;
      // Push cards into random direction
      card.style.transform = `translate(${
        (100 + 100 * Math.random()) * direction1
      }vw, ${100 + 100 * Math.random() * direction2}vh)`;
    }, 500);
  });

  // Animate score text
  document.querySelector(".score-text").classList.add("game-over");

  // Fade out the screen
  playGameScreen.classList.add("game-over");

  return new Promise((resolve, reject) => {
    setTimeout(() => {
      // Hide screen
      playGameScreen.style.display = "none";
      resolve();
    }, 1500);
  });
};

const showGameOverScreen = () => {
  gameOverContainer.classList.add("game-over");
};

const handleGameOver = async () => {
  recordUserScore();
  showFinalScore();
  await hidePlayGameScreen();
  showGameOverScreen();
};

const checkGameState = () => {
  gameState.matchedPairs++;
  if (gameState.matchedPairs === +pairsCount) handleGameOver();
};

const compereCards = async () => {
  if (gameState.firstFlip === gameState.secondFlip) {
    animateMatch();
    handleScoreIncrement();
    checkGameState();
  } else {
    resetConsecutivePairs();
    await animateNoMatch();
  }
  gameState = {
    ...gameState,
    firstFlip: "",
    firstFlipId: "",
    secondFlip: "",
    secondFlipId: "",
    compering: false,
  };
};

const handleClickOnCard = (e) => {
  const clickedCard = e.target;
  // Prevent double click on already flipped card and matched ones
  if (
    clickedCard.nodeName === "IMG" ||
    clickedCard.id === gameState.firstFlipId ||
    clickedCard.id === gameState.secondFlipId
  )
    return;
  if (!gameState.firstFlip || !gameState.secondFlip) flipCard(clickedCard);
  // When two cards are flipped compere them, timout for animation
  if (gameState.firstFlip && gameState.secondFlip && !gameState.compering) {
    gameState.compering = true;
    setTimeout(compereCards, 500);
  }
};

const likeImage = async (image, url, author, username) => {
  if (username === "Stranger") return;

  const data = {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ image, url, author, username }),
  };

  try {
    await fetch("/getlikes", data);
  } catch (err) {
    console.log(err);
  }
};

const handleLikeButtonClick = (e) => {
  const likeButton = e.target;
  const childArr = [...likeButton.parentNode.childNodes];
  const [image] = childArr.filter((item) => item.nodeName === "IMG");
  const [link] = childArr.filter((item) => item.nodeName === "A");
  const [author] = childArr.filter((item) => item.nodeName === "DIV");

  likeButton.removeEventListener("click", handleLikeButtonClick);
  likeButton.parentNode.classList.add("liked");
  likeButton.innerText = "Liked";

  likeImage(image.src, link.href, author.id, username);
};

const init = () => {
  assignClassAccordingToPairs(pairsCount);
  gameCardContainer.addEventListener("click", handleClickOnCard);
  likeButtons.forEach((button) => {
    button.addEventListener("click", handleLikeButtonClick);
  });
  calculateTimeBonusBase();
};

init();
