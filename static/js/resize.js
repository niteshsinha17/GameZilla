const games_wrapper = document.querySelector(".games");

const games = document.querySelectorAll(".g-card");
// After Loading Documents get games
let old_size;
const loaded = () => {
  games.forEach((element) => {
    $(element).hide();
  });
  let width = window.innerWidth;
  if (width > 1236) {
    arrange_games(3);
  } else if (width > 500) {
    arrange_games(2);
  } else {
    arrange_games(1);
  }
  old_size = width;
  $(document.querySelector(".stage")).addClass("hide-stage");
};

// It will render page when we will resize page
window.addEventListener("resize", () => {
  let width = window.innerWidth;
  if (width > 1236 && old_size < 1236) {
    arrange_games(3);
  } else if (
    width > 500 &&
    (old_size < 500 || old_size > 1236) &&
    width < 1236
  ) {
    arrange_games(2);
  } else if (width < 500 && old_size > 500) {
    arrange_games(1);
  }
  old_size = width;
});

const arrange_games = (n) => {
  console.log("arrage");
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
    games_wrapper.appendChild(row);
  }

  if (extra > 0) {
    let row = document.createElement("div");
    row.setAttribute("class", "row");
    while (count < games.length) {
      row.appendChild(games[count]);
      count++;
    }

    games_wrapper.appendChild(row);
  }

  games.forEach((element) => {
    $(element).show();
  });
};
