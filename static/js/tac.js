/* jshint browser: true */
/*jshint esversion: 6 */

// INITIAL SETUP
var music_stoped = true;
var sound_stoped = true;
const current_player = document.querySelector(".current_player");
const timer = document.querySelector(".timer");
const music = document.getElementById("tac_music");
var state;
var sent = false;
var chat_open = false;
// timer variables
var timer_, stop_timer_, no_respose_timer, change_player_timer;
var unread = 0;
var t = 12;
var boxes = document.querySelectorAll('.TAC__box');
(function ($) {
  // "use strict";
  $(document).ready(function () {
    scrollBottom();
    initialization();
    setRotate($);
    $(window).bind("resize", function () {
      screenOrientation = ($(window).width() > $(window).height()) ? 90 : 0;
      // 90 means landscape, 0 means portrait
      setRotate($);
    });
  });
})(jQuery);


function setRotate($) {
  screenOrientation = ($(window).width() > $(window).height()) ? 90 : 0;
  // 90 means landscape, 0 means portrait
  if (screenOrientation === 0) {
    $('.rotate').removeClass('rotate-hide');
  }
  else {
    $('.rotate').addClass('rotate-hide');
  }
}

function initialization() {
  for (let i = 0; i < 3; i++) {
    for (let j = 0; j < 3; j++) {
      if (board[i][j] !== 0) {
        addIcon(i, j);
      }
    }
  }
}

$('.TAC__box').click(function (e) {
  // player click on box
  animateBox(e.target);
  if (state.current_player === details.me && !sent) {
    let position = getIndex(e.target);
    let i = Math.floor(position / 3);
    let j = Math.floor(position % 3);
    if (board[i][j] !== 0) {
      notification('Invalid Move');
      soundIntrupt("sound_notification");
      return;
    }
    clearTimer();
    clearTimeout(change_player_timer);
    sent = false;
    socket.send(JSON.stringify({
      action: 'play',
      i: i,
      j: j
    }));
    if (details.is_zero) {
      addZero(e.target);
    }
    else {
      addCross(e.target);
    }
  }
  else {
    notification('Wait for your Turn');
    soundIntrupt("sound_notification");
    return;
  }
});

function addIcon(i, j) {
  if (board[i][j] === 'Z') {
    addZero(boxes[3 * i + j]);
  }
  else {
    addCross(boxes[3 * i + j]);
  }
}

function addZero(box) {
  $(box).html('<div class="box_zero" ></div>');
  soundIntrupt('sound_circle');
}

function addCross(box) {
  $(box).html('<div class="box_cross" ></div>');
}

function getIndex(box) {
  for (let index = 0; index < boxes.length; index++) {
    const element = boxes[index];
    if (element === box) {
      return index;
    }
  }
}

function animateBox(box) {
  $(box).css({ 'background': '#0000003d' });
  setTimeout(function () {
    $(box).css({ 'background': 'transparent' });
  }, 200);
}

function mark(data) {
  board = data.board;
  if (data.player === details.me) {
    return;
  }
  let position = data.i * 3 + data.j;
  if (details.is_zero) {
    addCross(boxes[position]);
  }
  else {
    addZero(boxes[position]);
  }
}

function player_not_joined(data) {
  if (data.player === details.me) {
    $(".loading_msg").html(
      "Unable to connect, redirecting to room in 2secs.."
    );
    setTimeout(function () {
      window.location.href = "/room/" + ROOM_NO;
    }, 2000);
  }
  else {
    msg = `<div class="winner">
    <div class="winner__heading">Game Over</div>
    <div class="winner__msg">
      <div winner__icon>
        Players not joined
      </div>
    </div>
    <div class="winner__loading">Redirecting to room in 5sec..</div>
    </div>`;
    showGameOver(msg);
    setTimeout(function () {
      window.location.href = "/room/" + ROOM_NO;
    }, 2000);
  }
}

function soundIntrupt(sound) {
  if (sound_stoped) {
    return;
  }
  if (!music_stoped) {
    music.voloum = 0.01;
  }
  $('#' + sound)[0].play();
  setTimeout(function () {
    if (!music_stoped) {
      music.voloum = 1;
    }
  });
}

function online(data) {
  if (data.status) {
    $("#l_" + data.player + ' .player__active').removeClass('offline');
  } else {
    $("#l_" + data.player + ' .player__active').addClass('offline');
  }
}

function message(data) {
  other = data.sender === details.me ? "" : "other";
  $(".chat__messages").append(`<div class="chat__message ${other} ">
      <h5 class="chat__sender">${data.sender}</h5>
      <p class="chat__msg ${other}">
      ${data.msg}
      </p>
    </div>`);
  if (data.sender != details.me && !chat_open) {
    unread++;
    $(".unread").html(unread);
    if (unread === 1) {
      $(".unread").addClass("show_unread");
    }
  }
  scrollBottom();
  if (data.sender !== details.me) {
    soundIntrupt("sound_msg");
  }
}

function playersNotJoined(data) {
  if (data.player === details.me) {
    $('.loading_msg').html('Unable to Connect, Redirecting to room in 2sec..');
    setTimeout(function () {
      window.location.href = "/room/" + ROOM_NO;
    }, 2000);
    return;
  }
  let class_name = details.is_zero ? 'zero' : 'cross';
  showGameOver(`<div class="winner">
  <div class="winner__heading">Game Over</div>
  <div class="winner__msg">
    <div winner__icon>
      <div class="box_${class_name}"></div>
    </div>
    wins the game, Other player not joined
  </div>
  <div class="winner__loading">Redirecting to room in 5sec..</div>
  </div>`);
}

function sendMessage() {
  msg = $("#message").val();
  if (msg.length > 0) {
    $("#message").val("");
    socket.send(
      JSON.stringify({
        action: "message",
        message: msg,
      })
    );
  }
}

$("#message").on("keyup", (event) => {
  if (event.keyCode === 13) {
    msg = $("#message").val();
    if (msg.length > 0) {
      $("#message").val("");
      socket.send(
        JSON.stringify({
          action: "message",
          message: msg,
        })
      );
    }
  }

});

function leave() {
  $('.backdrop').removeClass('hide-backdrop');
  $('.backdrop').append('<div class="loader"></div>');
  socket.send(
    JSON.stringify({
      action: "leave",
    })
  );
}

function startTimer() {
  t = state.time;
  stop_timer_ = setTimeout(function () {
    clearInterval(timer_);
  }, t * 1000);
  timer_ = setInterval(function () {
    t--;
    timer.innerText = t;
  }, 1000);
}

function clearTimer() {
  if (timer_) {
    clearInterval(timer_);
  }
  if (stop_timer_) {
    clearTimeout(stop_timer_);
  }
}

function showState() {
  current_player.innerText = state.current_player;
}

function started(data) {
  state = data.state;
  board = data.board;
  showState();
  startTimer();
  if (state.current_player == details.me) {
    sent = false;
    change_player_timer = setTimeout(function () {
      sent = true;
      change_player();
    }, state.time * 1000);
  } else {
    no_respose_timer = setTimeout(function () {
      socket.send(
        JSON.stringify({ action: "check_state", old_state: state })
      );
    }, state.time * 1000 + 4000);
  }
}

function change_player() {
  socket.send(JSON.stringify({ action: "change_player" }));
}

function handle_sound(event) {
  animateBtn(event.target);
  sound_stoped = !sound_stoped;
  if (sound_stoped) {
    $(event.target).removeClass("on");
  } else {
    $(event.target).addClass("on");
  }

}

function handle_music(event) {
  animateBtn(event.target);
  if (music_stoped) {
    music.play();
    $(event.target).addClass("on");
  } else {
    music.pause();
    $(event.target).removeClass("on");
  }
  music_stoped = !music_stoped;

}

function handle_exit(event) {
  $('.exit').addClass("show_exit");
  soundIntrupt("sound_notification");
  animateBtn(event.target);

}

document.querySelector(".stay").addEventListener("click", function (e) {
  $('.exit').removeClass("show_exit");
});

function handle_chat(event) {
  chat_open = !chat_open;
  if (chat_open) {
    readMessage();
    $('#message').focus();
  }
  $(document.querySelector(".chat")).toggleClass("show_chat");
  animateBtn(event.target);

}

function scrollBottom() {
  msg = document.querySelector(".chat__messages");
  msg.scrollTop = msg.scrollHeight;
}

function readMessage() {
  if (unread > 0) {
    $(".unread").removeClass("show_unread");
    unread = 0;
  }
}

function animateBtn(btn) {
  $(btn).addClass("animate_btn");
  setTimeout(function () {
    $(btn).removeClass("animate_btn");
  }, 100);
}

function notification(msg) {
  let l = document.querySelectorAll(".notification").length;
  $(".TAC__notification").append(get_notification_object(l, msg));
  setTimeout(function () {
    $(`#n_${l}`).slideUp(500, function () {
      $(`#n_${l}`).remove();
    });
  }, 3000);
}
function get_notification_object(l, msg) {
  return `<li class="notification" id="n_${l}">
      <button class="notification__btn">
        <img class="notification__bell" src="/static/icons/bell.png" alt="" />
      </button>
      <div class="notification__msg">${msg}</div>
    </li>`;
}

function game_over(data) {
  let msg;
  if (data.win) {
    markWinLine(data);
    msg = createWinMessage(data);
  }
  else {
    msg = createDrawMessage();
  }
  showGameOver(msg);
}

function createWinMessage(data) {
  let class_name = board[data.i][data.j] === 'X' ? 'cross' : 'zero';
  return `<div class="winner">
  <div class="winner__heading">Game Over</div>
  <div class="winner__msg">
    <div winner__icon>
      <div class="box_${class_name}"></div>
    </div>
    wins the game
  </div>
  <div class="winner__loading">Redirecting to room in 5sec..</div>
  </div>`;
}
function leaved(data){
  let class_name = data.player === 'X' ? 'cross' : 'zero';
  if(data.player_name===details.me){

     window.location.href='/room/'+ROOM_NO;
     return;
  }
  let msg = `<div class="winner">
  <div class="winner__heading">Game Over</div>
  <div class="winner__msg">
    <div winner__icon>
      <div class="box_${class_name}"></div>
    </div>
    leaved the game
  </div>
  <div class="winner__loading">Redirecting to room in 5sec..</div>
  </div>`;
    showGameOver(msg);
}

function createDrawMessage() {
  return `<div class="winner">
  <div class="winner__heading">Game Over</div>
  <div class="winner__msg">
    Draw
  <div class="winner__loading">Redirecting to room in 5sec..</div>
  </div>`;
}

function showGameOver(msg) {
  setTimeout(function () {    
  $('.backdrop').removeClass('hide-backdrop');
    $('body').append(msg);
    soundIntrupt('sound_win');
    setTimeout(function () {
      window.location.href = "/room/" + ROOM_NO;
    }, 5000);
  }, 1000);
}
function markWinLine(data) {
  if (data.tilt) {
    addTiltLine(data);
  }
  else {
    addStLine(data);
  }
}

function addStLine(data) {
  let left, top;
  if (data.horizontal) {
    top = 70 * data.position + 35;
    left = 0;
    $('.board').append(
      `<div style="left:${left}px; top:${top}px;" class='h-line'></div>
      
      `
    );
  }
  else {
    left = 70 * data.position + 35;
    top = 0;
    $('.board').append(
      `<div style="left:${left}px; top:${top}px;"  class='v-line'></div>
      `
    );
  }

}

function addTiltLine(data) {
  if (data.position == 0) {
    $('.board').append(
      `<div class='t-line-f-top'></div>
      `
    );
  }
  else {
    $('.board').append(
      `<div class='t-line-f-bottom'></div>
      `
    );
  }
}