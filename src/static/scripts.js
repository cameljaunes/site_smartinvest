/*!
* Start Bootstrap - Creative v7.0.7 (https://startbootstrap.com/theme/creative)
* Copyright 2013-2023 Start Bootstrap
* Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-creative/blob/master/LICENSE)
*/
//
// Scripts
// 

window.addEventListener('DOMContentLoaded', event => {

    // Navbar shrink function
    var navbarShrink = function () {
        const navbarCollapsible = document.body.querySelector('#mainNav');
        if (!navbarCollapsible) {
            return;
        }
        if (window.scrollY === 0) {
            navbarCollapsible.classList.remove('navbar-shrink')
        } else {
            navbarCollapsible.classList.add('navbar-shrink')
        }

    };

    // Shrink the navbar 
    navbarShrink();

    // Shrink the navbar when page is scrolled
    document.addEventListener('scroll', navbarShrink);

    // Activate Bootstrap scrollspy on the main nav element
    const mainNav = document.body.querySelector('#mainNav');
    if (mainNav) {
        new bootstrap.ScrollSpy(document.body, {
            target: '#mainNav',
            rootMargin: '0px 0px -40%',
        });
    };

    // Collapse responsive navbar when toggler is visible
    const navbarToggler = document.body.querySelector('.navbar-toggler');
    const responsiveNavItems = [].slice.call(
        document.querySelectorAll('#navbarResponsive .nav-link')
    );
    responsiveNavItems.map(function (responsiveNavItem) {
        responsiveNavItem.addEventListener('click', () => {
            if (window.getComputedStyle(navbarToggler).display !== 'none') {
                navbarToggler.click();
            }
        });
    });

    // Activate SimpleLightbox plugin for portfolio items
    new SimpleLightbox({
        elements: '#portfolio a.portfolio-box'
    });

});

//MON JAVA SCRIPT

// Afficher la valeur de la jauge en temps réel
const jauge1 = document.getElementById('jaugeA');
const valeurJauge1 = document.getElementById('valeurAnnimation');

jauge1.addEventListener('input', function() {
valeurJauge1.textContent = jauge1.value;
});

const jauge2 = document.getElementById('jaugeS');
const valeurJauge2 = document.getElementById('valeurSecurité');

jauge2.addEventListener('input', function() {
valeurJauge2.textContent = jauge2.value;
});

const jaugeSurface = document.getElementById('jaugeSurface');
const valeurSurface = document.getElementById('valeurSurface');

jaugeSurface.addEventListener('input', function() {
valeurSurface.textContent = jaugeSurface.value;
});


const jauge3 = document.getElementById('budget');
const valeurJauge3 = document.getElementById('valeurBudget');

jauge3.addEventListener('input', function() {
valeurJauge3.textContent = jauge3.value;
});

// Fonction pour afficher les pop-up
    function PopupQuartier() {
      alert("Pop-up : Vous devriez investir à Ramonville");
    };



