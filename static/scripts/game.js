// Because of Jinja syntax, const pairs must have been assigned in game.html.

// <script type="text/javascript">
//   const pairs = "{{ pairs }}"
// </script>
const gameCardContainer = document.querySelector(".game-cards-container");

const assignClassAccordingToPairs = (pairsCount) => {
  switch (pairsCount) {
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
  assignClassAccordingToPairs(pairs);
};

init();
