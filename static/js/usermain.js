const closeBtn = document.querySelector(".btn");
const sidenav = document.querySelector("sidenav");
const closeSideNav = document.querySelector(".closeSideNav");

closeBtn.addEventListener("click" , function() {
    sidenav.classList.remove("hidden");
})