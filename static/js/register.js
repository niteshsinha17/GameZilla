/* jshint browser: true */
/*jshint esversion: 6 */

// variables for slider
var currentSlide = 0;
const sliders = document.querySelectorAll(".s_slider");

// variables for register form
const register = document.querySelector(".register");
const regitration_form = document.querySelector("#form");

(function ($) {
  // "use strict";
  $(document).ready(function () {
    removeLoader($);
    initSlider($);
    initFormHandler($);
    initFormValidation($);
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

function initFormHandler($) {
  function showRegister($) {
    $(register).addClass("active");
    $(regitration_form).addClass("active");
    $(regitration_form).removeClass("hide");
  }
  function hideRegister($) {
    $(register).removeClass("active");
    $(regitration_form).removeClass("active");
    $(regitration_form).addClass("hide");
  }
  $('#login_btn').click(function () {
    // slide down the registration page
    hideRegister($);
  });

  $('#register_btn').click(function () {
    // slide up the registration page
    showRegister($);
  });

  $('#registration_form input').on('focus', function () {
    if (!$(register).hasClass('active')) {
      showRegister($);
    }
  });

  $('#btn_register').click(function (e) {
    let username = $('#id_username').val();
    if (username.length < 5 | username.length > 8) {
      showMessage('username should be greater than 5 and less than 8 charecters');
      e.preventDefault();
      return;
    }
    if ($('#id_password1').val() !== $('#id_password').val()) {
      showMessage("password doesn't match");
      e.preventDefault();
      return;
    }
  });
}


function showMessage(msg, css = null) {
  let m = document.createElement("div");
  m.innerText = msg;
  m.setAttribute("class", "message");
  if (css) {
    $(m).css(css);
  }
  $('body').append(m);
  setTimeout(function () {
    $(m).slideUp(500, function () {
      $(m).remove();
    });
  }, 5000);
}

function initSlider($) {
  // handles changing of slides
  setInterval(function () {
    $(sliders[currentSlide]).removeClass("s-active");
    currentSlide++;
    if (currentSlide == sliders.length) {
      currentSlide = 0;
    }
    $(sliders[currentSlide]).addClass("s-active");
  }, 5000);
}

function initFormValidation($) {
  $('#id_username').on('keyup', function (e) {
    let value = e.target.value;
    if (value.length < 5 | value.length > 8) {
      $(e.target).css('border', '1px solid red');
    }
    else {
      $(e.target).css('border', '1px solid #ccd0d5');

    }
  });

  $('#id_password2').on('keyup', function (e) {
    if (e.target.value !== $('#id_password1').val()) {
      $(e.target).css('border', '1px solid red');
    }
    else {
      $(e.target).css('border', '1px solid #ccd0d5');

    }
  });
}
function removeLoader($) {
  $(".spiner").addClass("hide-spiner");
}