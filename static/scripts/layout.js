const navbarButton = document.getElementById("navbar-button");
const navbarList = document.getElementById("navbar-list");

navbarButton.addEventListener("click", () => {
  navbarList.classList.toggle("closed");
  navbarButton.classList.toggle("clicked");
});
