/* jshint browser: true */
/*jshint esversion: 6 */

// variables for game cards
const gameWrapper = document.querySelector(".games");
const games = document.querySelectorAll(".g-card");
var old_size;
function resizeOnLoad($) {
  // runs whwn window is loaded
  games.forEach((element) => {
    $(element).hide();
  });
  let width = window.innerWidth;
  if (width > 1236) {
    arrageGames(3);
  } else if (width > 500) {
    arrageGames(2);
  } else {
    arrageGames(1);
  }
  old_size = width;
}

function initOnResize($) {
  // change games view on resize
  $(window).on("resize", () => {
    let width = window.innerWidth;
    if (width > 1236 && old_size < 1236) {
      arrageGames(3);
    } else if (
      width > 500 &&
      (old_size < 500 || old_size > 1236) &&
      width < 1236
    ) {
      arrageGames(2);
    } else if (width < 500 && old_size > 500) {
      arrageGames(1);
    }
    old_size = width;
  });
}

function arrageGames(n) {
  document.querySelectorAll(".row").forEach((element) => {
    element.remove();
  });
  row_ = Math.floor(games.length / n);
  extra = games.length % n;
  var count = 0;
  for (let i = 0; i < row_; i++) {
    let row = document.createElement("div");
    row.setAttribute("class", "row");
    for (let i = 0; i < n; i++) {
      row.appendChild(games[count]);
      count++;
    }
    gameWrapper.appendChild(row);
  }
  if (extra > 0) {
    let row = document.createElement("div");
    row.setAttribute("class", "row");
    while (count < games.length) {
      row.appendChild(games[count]);
      count++;
    }
    gameWrapper.appendChild(row);
  }
  games.forEach((element) => {
    $(element).show();
  });
}
