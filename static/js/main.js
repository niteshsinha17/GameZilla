// ////////////////////////
//     Navigation
// ///////////////////////

const navigation = document.querySelector(".navigation");
const navigation_icon = document.querySelector("#navigation-icon");
const navigation_toggler = document.querySelector(".navigation__toggler");

const navigationBarHandler = () => {
  $(navigation).toggleClass("nav-active");
  $(navigation_icon).toggleClass("active");
  $(navigation_toggler).toggleClass("toggler-animate");
};

// /////////////////
//   Register
// ///////////////

const register = document.querySelector(".register");
const regitration_form = document.querySelector("#form");
const guest_form = document.querySelector("#guest_form");
const show_register = () => {
  $(register).addClass("active");
  $(regitration_form).addClass("active");
  $(regitration_form).removeClass("hide");
};

const hide_register = () => {
  $(register).removeClass("active");
  $(regitration_form).removeClass("active");
  $(regitration_form).addClass("hide");
};

// const show_guest_form = () => {
//   $(guest_form).addClass("g-active");
// };

// ///////////////
//      slider
// //////////////
const sliders = document.querySelectorAll(".s_slider");

var current_s = 0;

setInterval(() => {
  $(sliders[current_s]).removeClass("s-active");
  current_s++;
  if (current_s == sliders.length) {
    current_s = 0;
  }
  $(sliders[current_s]).addClass("s-active");
}, 5000);

// //////////////////
//     join dropdown
// /////////////////
const join_dropwown = document.querySelector(".join_dropdown");

document.querySelector(".join__btn").addEventListener("click", () => {
  $(join_dropwown).addClass("join_dropdown-active");
});

document
  .querySelector(".join_dropdown__cross")
  .addEventListener("click", () => {
    $(join_dropwown).removeClass("join_dropdown-active");
  });
