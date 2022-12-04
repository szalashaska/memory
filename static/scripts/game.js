// Because of Jinja syntax, const pairs must have been assigned in game.html.

// <script type="text/javascript">
//   const pairs = "{{ pairs }}"
// </script>

let gameState = {
  firstFlip: "",
  firstFlipId: "",
  secondFlip: "",
  secondFlipId: "",
  score: 0,
  compering: false,
};

const gameCardContainer = document.querySelector(".game-cards-container");

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

const handleNoMatch = () => {
  console.log("2");
  const firstCard = document.getElementById(gameState.firstFlipId);
  const secondCard = document.getElementById(gameState.secondFlipId);
  firstCard.classList.add("no-match");
  secondCard.classList.add("no-match");
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      console.log("3");
      firstCard.classList.remove("no-match");
      secondCard.classList.remove("no-match");
      firstCard.classList.remove("flipped");
      secondCard.classList.remove("flipped");
      resolve();
    }, 1000);
  });
};

const handleMatch = () => {};

const compereCards = async () => {
  console.log("1");
  if (gameState.firstFlip === gameState.secondFlip) handleMatch();
  else await handleNoMatch();
  console.log("4");
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
  if (!gameState.firstFlip || !gameState.secondFlip) flipCard(clickedCard);
  if (gameState.firstFlip && gameState.secondFlip && !gameState.compering) {
    gameState.compering = true;
    setTimeout(compereCards, 500);
  }
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

const init = () => {
  assignClassAccordingToPairs(pairsCount);
  gameCardContainer.addEventListener("click", handleClickOnCard);
};

init();
