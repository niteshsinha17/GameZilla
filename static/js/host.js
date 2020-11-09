/* jshint browser: true */
/*jshint esversion: 6 */
const link =
    window.location.protocol + window.location.host + "/join/" + ROOM_NO;
const inviteMessage = `Hello, I welcome you to play game with me on GameZilla. Click on the bellow to join it. ${link}
        Game Id:  ${ROOM_NO}`;

const bg_games = document.querySelectorAll(".g-card__img");
const room = document.querySelector(".room__bg");
const error_ = document.querySelector(".error");
const members = document.querySelector(".members__list");

(function (
    $) {
    // "use strict";
    $(document).ready(function () {
        removeLoader($);
        // arrageGames(3);
        initDropdownHanders($);
        MessageHandlers($);
        set_start();
        addInviteMessage($);
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
function addInviteMessage($) {
    $('.room').append(
        `<textarea class="link_message" cols="10" rows="10"></textarea>
        `);
    $('textarea').val(inviteMessage);
}
function removeLoader($) {
    $(".spiner").addClass("hide-spiner");
}


function animateButton(btn) {
    $(btn).addClass("animate_btn");
    setTimeout(function () {
        $(btn).removeClass("animate_btn");
    }, 100);
}

function remove(event, member_name) {
    animateButton(event.target);
    socket.send(
        JSON.stringify({
            action: "remove_player",
            member: member_name,
        })
    );
}

$('.room__start').click(function (e) {
    animateButton(e.target);
    socket.send(JSON.stringify({ action: "start" }));
});

$('.room__leave').click(function (e) {
    animateButton(e.target);
    socket.send(JSON.stringify({ action: "leave" }));
});

function initDropdownHanders($) {
    // handles details show and hide
    $('.detail__cross').click(function (e) {
        animateButton(e.target);
        $(".room__detail").removeClass("show_detail");
    });

    $('#detail_icon').click(function () {
        $(".room__detail").addClass("show_detail");
    });

    $('#setting').click(function () {
        $('#setting').addClass("setting_active");
        $('.games_dropdown').addClass("games_dropdown-active");
    });

    $('.games_dropdown__cross').click(function () {
        $('#setting').removeClass("setting_active");
        $('.games_dropdown').removeClass("games_dropdown-active");
    });
}

function MessageHandlers($) {
    $('.room__share').click(function (e) {
        animateButton(e.target);
        $('textarea').focus();
        $('textarea').select();
        document.execCommand("copy");
        showMessage("link copied", { 'background': 'transparent', 'color': '#6464ff', 'top': '18px' });
    });
}

function showMessage(msg, css = null) {
    let m = document.createElement("div");
    m.innerText = msg;
    m.setAttribute("class", "message");
    if (css) {
        $(m).css(css);
    }
    $('.room').append(m);
    setTimeout(function () {
        $(m).slideUp(500, function () {
            $(m).remove();
        });
    }, 3000);
}

function started(data) {
    if (data.can_start) {
        window.location.href = data.url;
    }
    else {
        showMessage(data.error);
    }
}

function leaved(data) {
    if (data.member === state.me || data.member === "all") {
        window.location.href = "/";
    }
    else {
        remove_member(data);
    }
}

function add_member(data) {
    if (data.member === state.me) {
        return;
    }
    $(".members__list").append(create_member(data));
    if (data.ready) {
        state.members_ready += 1;
    }
    state.members_joined += 1;

    $('#members_joined').text(state.members_joined);
    set_start();
}

function create_member(data) {
    let r = data.ready ? "ready" : "not ready";
    return (`<li id="r_${data.member}" class="members__item">
                <div class="members_name">
                  ${data.member}
                  <span class="online">
                    offline
                  </span>
                </div>
                <div class="members__btns">
                  <button id="s_${data.member}" class="members__ready">
                   ${r}
                  </button>
                  <button onclick="remove(event,'${data.member}')"
                          class="members__remove">
                    Remove
                    </button>
                </div>
            </li>`
    );
}



function remove_member(data) {
    $("#r_" + data.member).remove();
    if (data.was_ready) {
        state.members_ready -= 1;
    }
    state.members_joined -= 1;

    $('#members_joined').text(state.members_joined);
    set_start();
}

function ready(data) {
    if (data.state) {
        document.getElementById("s_" + data.member).innerText = "READY";
        state.members_ready += 1;
    }
    else {
        document.getElementById("s_" + data.member).innerText = "NOT READY";
        state.members_ready -= 1;
    }
    set_start();
}

function set_start() {
    if (
        state.members_ready === state.members_joined &&
        state.members_joined > 1
    ) {
        $(".room__start").addClass("ready");
    } else {
        $(".room__start").removeClass("ready");
    }
}

function game_changed(data) {
    if (!data.changed) {
        showMessage(data.error);
        return;
    }
    room.style.background = "url(" + data.url + ")";
    $(".room__heading span").text(data.name);
    $('#max_member').text(data.max_members);
    $('#min_member').text(data.min_members);
    state.game_code = data.new_code;
    $('#' + data.old_code).removeClass("selected");
    $('#' + data.new_code).addClass("selected");
}

$('.g-card').click(function (e) {
    if (e.target.id === state.game_code) {
        return;
    }
    socket.send(
        JSON.stringify({
            action: "change_game",
            url: $('#img_' + e.target.id).attr('src'),
            code: e.target.id,
        })
    );
});