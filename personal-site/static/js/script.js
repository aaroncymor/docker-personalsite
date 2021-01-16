document.addEventListener('DOMContentLoaded', (e)=>{

});

let burgerMenu = document.querySelector('.burger-menu');
burgerMenu.addEventListener('click', (e)=>{
    burgerMenu.nextElementSibling.style.right = "0";
});

let closeMenu = document.querySelector('.close-menu');
closeMenu.addEventListener('click', (e)=>{
    closeMenu.parentElement.style.right = "-26rem";
});