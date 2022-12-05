// Because of Jinja syntax, "const user: string" must have been assigned in myaccount.html.

// <script type="text/javascript">
//   const user = "{{ username }}";
// </script>

const deleteButtons = document.querySelectorAll(".photo-card__button");

const handleDeletePhoto = async (e) => {
  // Get image link: button -> parrent div -> image
  const imageURL = e.target.parentNode.firstElementChild.src;

  // Prepare data; user is set in other file
  const data = {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ image: imageURL, username: user }),
  };

  const request = await fetch("/deletephoto", data);
  const response = await request;

  // Reload page
  if (response.ok) location.reload();
};

deleteButtons.forEach((button) => {
  button.addEventListener("click", handleDeletePhoto);
});
