/* jshint browser: true */
/*jshint esversion: 6 */

// variables for navigation
const navigation = document.querySelector('.navigation');
const navigation_icon = document.querySelector('#navigation-icon');
const navigation_toggler = document.querySelector('.navigation__toggler');
var screenOrientation;
(function ($) {
  'use strict';
  $(document).ready(function () {
    resizeOnLoad($);
    removeLoader($);
    initOnResize($);
    joinHandler($);
    navigationBarHandler($);
    initAjaxCalls($);
    removeMessages($);
    setRotate($);
    initGameHandlet($);
    $(window).bind('resize', function () {
      screenOrientation = $(window).width() > $(window).height() ? 90 : 0;
      // 90 means landscape, 0 means portrait
      setRotate($);
    });
  });
})(jQuery);

function initGameHandlet($) {
  $('.g-card').on('click', function () {
    $('.backdrop').removeClass('hide-backdrop');
  });
}
function setRotate($) {
  screenOrientation = $(window).width() > $(window).height() ? 90 : 0;
  // 90 means landscape, 0 means portrait
  if (screenOrientation === 0) {
    $('.rotate').removeClass('rotate-hide');
  } else {
    $('.rotate').addClass('rotate-hide');
  }
}
function removeLoader($) {
  $('.spiner').addClass('hide-spiner');
}

function joinHandler($) {
  $('.join__btn').on('click', function (e) {
    e.stopPropagation();
    $('#id_input').focus();
    $('.join_dropdown').addClass('join_dropdown-active');
  });

  $('.join_dropdown__cross').on('click', function (e) {
    e.stopPropagation();
    $('.join_dropdown').removeClass('join_dropdown-active');
  });

  $(document).click(function (e) {
    e.stopPropagation();
    // Check if the clicked area is join_dropDown or not
    if ($('.join_dropdown').has(e.target).length === 0) {
      $('.join_dropdown').removeClass('join_dropdown-active');
    }
  });
  $('#join_form').on('submit', function (e) {
    game_id = $('#id_input').val();
    if (game_id.length !== game_id.split(' ').join('').length) {
      let m = document.createElement('div');
      $(m).addClass('message');
      $(m).text('invalid game id');
      $('body').append(m);
      removeMessage(m);
      e.preventDefault();
    }
  });
}

function navigationBarHandler($) {
  $('.navigation__toggler').click(function () {
    $(navigation).toggleClass('nav-active');
    $(navigation_icon).toggleClass('active');
    $(navigation_toggler).toggleClass('toggler-animate');
  });
}

function initAjaxCalls($) {
  function animateButton(btn) {
    // used to animate buttons on click
    $(btn).addClass('animate_btn');
    setTimeout(() => {
      $(btn).removeClass('animate_btn');
    }, 100);
  }

  $('.room__leave').click(function (e) {
    animateButton(e.target);
    id = e.target.id;
    let spinner = `<div id='spinner_${id}' class="room__cover">
                        <div class="loader"></div>
                     </div>`;
    $('#room_' + id).append(spinner);
    $.get('/leave/' + id, function (data) {
      let data_ = JSON.parse(data);
      if (data_.deleted) {
        $('#room_' + id).remove();
      } else {
        $('#spinner_' + id).remove();
      }
      let m = document.createElement('div');
      $(m).addClass('message');
      $(m).text(data_.reason);
      $('body').append(m);
      removeMessage(m);
    });
  });
}

function removeMessages($) {
  removeMessage('.message');
}

function removeMessage(m) {
  setTimeout(function () {
    $(m).slideUp(500, function () {
      $(m).remove();
    });
  }, 3000);
}
