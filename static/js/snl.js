/* jshint browser: true */
/*jshint esversion: 6 */

// INITIAL SETUP
var music_stoped = true;
var sound_stoped = true;
const current_player = document.querySelector(".current_player");
const timer = document.querySelector(".timer");
const dice = document.querySelector(".SNL__dice");
const music = document.getElementById("snl_music");
var state;
var sent = false;
var chat_open = false;

// default variables
const mobile = window.innerWidth < 942;
const defaultChange = mobile ? 30 : 50;
const defaultLeft = mobile ? 5 : 10;
const defaultBottom = mobile ? 5 : 10;
const defaultWidth = mobile ? 20 : 30;

var unread = 0;
var t = 12;

(function ($) {
  // "use strict";
  $(document).ready(function () {
    scrollBottom();
    setRotate($);
    exitHandlers($)
    $(window).bind("resize", function () {
      screenOrientation = ($(window).width() > $(window).height()) ? 90 : 0;
      // 90 means landscape, 0 means portrait
      setRotate($);
    });
  });
})(jQuery);

function exitHandlers($){
  $('.winners__room').on('click',function(e){
    e.preventDefault()
    console.log('here--------');
    window.location.href = '/room/'+ ROOM_NO;
  })
  $('.winners__exit').on('click',function(e){
    e.preventDefault()
    window.location.href = '/'
  })
}
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

function game_over(data) {
  if (data.leaved) {
    leaved(data);
    addLeaveMessage(data.leaved_msg);
    if(data.memeber===me){   //member denotes who leaved the game
      window.location.href = "/";
      return;
    }
  }
  else if (data.win) {
    move(data, data.position);
  }
  setTimeout(function () {
    soundIntrupt("sound_win");
    showWinners(data.winners);

    setTimeout(function () {
      window.location.href = "/room/" + ROOM_NO;
    }, 5000);
    let t = 5;
    let win_timer = setInterval(() => {
      if (t < 1) {
        clearInterval(win_timer);
        return;
      }
      t--;
      $('.winners__time').text(t);
    }, 1000);
  }, 2000);

}

function addLeaveMessage(leaved_msg) {
  $('.winners__leaved').text(leaved_msg);
}

function showWinners(winners) {
  $('.backdrop').removeClass('hide-backdrop');
  data = "";
  winners.forEach((winner) => {
    data += getWinner(winner);
  });
  $(".winners__wrapper").html(data);
  $('.winners').slideDown(500, function () {
    $('.winner_animate_div').addClass('winner_animate');
  });
}

function getWinner(winner) {
  rank = winner.rank !== null ? winner.rank : "Loser";
  return `<div class="winner">
        <div class="winners__img">
       ${rank}
        </div>
        <div class="winners__name">
          ${winner.name}
        </div>
      </div>`;
}

function leaved(data) {
  if (data.member === me) {
    if(data.remove){
      // this code may not be needed
      notification('you are removed');
    }
    return (window.location.href = "/room/"+ROOM_NO);
  }
  $(`#p_${data.member}`).addClass("disable");
  $(`#l_${data.member}`).addClass("disable");
  notification(data.leaved_msg);
  if (data.start) {
    started(data);
  }
}

function message(data) {
  other = data.sender === me ? "" : "other";
  $(".chat__messages").append(`<div class="chat__message ${other} ">
      <h5 class="chat__sender">${data.sender}</h5>
      <p class="chat__msg ${other}">
      ${data.msg}
      </p>
    </div>`);

  if (data.sender != me && !chat_open) {
    unread++;
    $(".unread").html(unread);
    if (unread === 1) {
      $(".unread").addClass("show_unread");
    }
  }
  scrollBottom();
  if (data.sender !== me) {
    soundIntrupt("sound_msg");
  }
}

function player_not_joined(data) {
  data.players.forEach(player => {
    if (player.member===me){
      $('.loading_msg').html('Unable to Connect, Redirecting to room in 2sec');
      setTimeout(function () {
        window.location.href = "/room/" + ROOM_NO;
      }, 2000);
      return;
    }
    if ($(".spiner").length) {
      // remove spinner
      $(".spiner").remove();
    }
    setTimeout(function(){      
    $(`#p_${player.member}`).addClass("disable");
    $(`#l_${player.member}`).addClass("disable");    
    online({'member':player.member,'status':false});
    notification(player.member+' was removed due to network');
    },1000);

  });
  notification('Redirecting to room in 4sec');
  setTimeout(function () {
    window.location.href = "/room/" + ROOM_NO;
  }, 4000);
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

function remove_players(players){
  players.forEach(player => {
    if (player.member === me){
      window.location.href='/';
      return;
    }
    $(`#p_${player.member}`).addClass("disable");
    $(`#l_${player.member}`).addClass("disable");    
    online({'member':player.member,'status':false});
    notification(player.member+' was removed due to network');
  });
}

function leave() {
  clearTimer();
  clearTimeout(change_player_timer);  
  $('.backdrop').removeClass('hide-backdrop');
  $('.backdrop').append('<div class="loader"></div>');
  socket.send(
    JSON.stringify({
      action: "leave",
    })
  );
}

function showDice(no) {
  $(dice).html(no);
}

function cant_move(data) {
  showDice(data.number);
  if (data.player === me) {
    notification(data.error_msg);
  }
  started(data);
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

function showState() {
  // it will show state 
  current_player.innerText = state.current_player;
}

function win(data) {
  $('#l_' + data.winner).append(`<div class='player__rank'>${data.rank}</div>`);
  if (me === data.winner) {
    $('#play').addClass('disable');
  }
}

function started(data) {
  state = data.state;
  showState();
  startTimer();
  if (state.current_player === me) {
    sent = false;
    change_player_timer = setTimeout(function () {
      sent = true;
      change_player();
    }, state.time * 1000);
    // setTimeout(play,2000);
  } else {
    no_respose_timer = setTimeout(function () {
      socket.send(
        JSON.stringify({ action: "check_state", old_state: state })
      );
    }, state.time * 1000 + 2000 + player_no*1000);
  }
}

function play(e) {
  animateBtn(e.target);
  if (!sent && state.current_player === me) {
    clearTimer();
    clearTimeout(change_player_timer);
    sent = false;
    socket.send(JSON.stringify({ action: "play" }));
  } else {
    notification("wait for your turn");
    soundIntrupt("sound_notification");
  }

}

function move(data, position) {
  p = position;
  player = data.player;
  if (p <= 10) {
    set_position(player, p - 1, 0);
  } else {
    b = Math.floor(p / 10);
    reminder = p % 10;
    if (reminder === 0) {
      b--;
    }
    if (b % 2 === 0) {
      if (reminder === 0) {
        reminder = 10;
      }
      set_position(player, reminder - 1, b);
    } else {
      if (reminder === 0) {
        reminder = 10;
      }
      set_position(player, 10 - reminder, b);
    }
  }
}

function double_move(data) {
  move(data, data.position);
  setTimeout(function () {
    if (data.bridge === "SNAKE") {
      soundIntrupt("sound_snake");
    } else {
      soundIntrupt("sound_ladder");
    }
    move(data, data.bridge_end);
  }, 500);
}

function change_player() {
  socket.send(JSON.stringify({ action: "change_player" }));
}

function open_player(data) {
  soundIntrupt("sound_open");
  $("#p_" + data.player).animate({
    opacity: 1,
    left: defaultLeft + "px",
    bottom: defaultBottom + "px",
    width: defaultWidth + "px",
    height: defaultWidth + "px",
  });
  started(data);
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

document.querySelector(".stay").addEventListener("click", function () {
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
  $(".SNL__notification").append(get_notification_object(l, msg));
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