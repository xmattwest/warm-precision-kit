/* Example pages: show or hide the decision notes beside an artifact.
   Notes are visible without script; the button only appears when it works. */
(function () {
  "use strict";
  document.querySelectorAll(".ex-annotated").forEach(function (block) {
    var bar = block.querySelector(".ex-toggle");
    var button = bar && bar.querySelector("button");
    if (!button) return;
    function render() {
      var off = block.classList.contains("notes-off");
      button.textContent = off ? "Show the notes" : "Hide the notes";
      button.setAttribute("aria-pressed", String(!off));
    }
    button.addEventListener("click", function () {
      block.classList.toggle("notes-off");
      render();
    });
    bar.hidden = false;
    render();
  });
})();
