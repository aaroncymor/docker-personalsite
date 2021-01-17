AOS.init({
    duration: 1200,
    once: true
});

window.onbeforeunload = function () {
    window.scrollTo(0, 0);
}

/**
 * Loader Animation
 */
setTimeout(()=>{
    document.body.style.overflow = "auto";
    const loaderSection = document.querySelector('.loader');
    loaderSection.style.display = "none";
}, 5000);

/**
 * Menu Section Animation
 */

const menuBurger = document.querySelector(".burger-menu");
menuBurger.addEventListener('click', (e)=>{
    e.preventDefault();
    document.querySelector('.nav').classList.add("open");
});

const menuClose = document.querySelector(".close-menu");
menuClose.addEventListener('click', (e)=>{
    e.preventDefault();
    const nav = e.target.parentElement.parentElement;
    nav.classList.remove("open");
});

let currNavIndex = 0;
const navLinks = document.querySelectorAll('.menu-nav__link');
navLinks.forEach((navLink, index)=>{
    navLink.addEventListener('click', (e)=>{
        // remove active class to previous nav link
        navLinks[currNavIndex].classList.remove("active");

        // assign new value of navIndex
        currNavIndex = index;

        // add active class to current nav link
        navLink.classList.add("active");
        const nav = e.target.parentElement.parentElement.parentElement;
        nav.classList.remove("open");
    });
});


const sections = document.querySelectorAll("section:not(.loader)");
// https://css-tricks.com/a-few-functional-uses-for-intersection-observer-to-know-when-an-element-is-in-view/
if(!!window.IntersectionObserver){
    let observer = new IntersectionObserver((entries, observer)=>{
        entries.forEach(entry=>{
            if(entry.isIntersecting){

                // remove active class to previous nav link
                navLinks[currNavIndex].classList.remove("active");

                // assign new value of navIndex
                currNavIndex = entry.target.dataset.navIndex;

                // add active class to current nav link
                navLinks[currNavIndex].classList.add("active");
            }
        });
    }, {threshold: .25});

    sections.forEach(section=>{
        observer.observe(section);
    });
} else {

}


/**
 * Skills Section Animation
 */
var skillIndex = 0;
skillList = [
    '.skills__html5',
    '.skills__css',
    '.skills__js',
    '.skills__python',
    '.skills__php',
    '.skills__sql',
    '.skills__devops',
    '.skills__os',
    '.skills__mobile'
];
techList = [
    '.html-tech',
    '.css-tech',
    '.js-tech',
    '.python-tech',
    '.php-tech',
    '.sql-tech',
    '.devops-tech',
    '.os-tech',
    '.mobile-tech'
];

// every x seconds, add highlight to target div, and
// add fade/hide to target lists
setInterval(()=>{
    if (skillIndex < skillList.length) {

        // index to remove added highlight and hide classes
        // from div.skills__<name> and li.<name>-tech
        // if current skillIndex -1 is less than 0, we assign
        // last element index, else it will be current skill index - 1
        var removeIndex = skillIndex - 1 < 0 
            ? skillList.length - 1
            : skillIndex - 1;
        
        document.querySelector(skillList[removeIndex])
            .classList.remove("enlarge");

        // remove highlight and hide classes with removeIndex
        document.querySelectorAll(`li${techList[removeIndex]}`)
        .forEach((li, item)=>{
            li.classList.remove("highlight");
        });

        document.querySelectorAll(`.skills__tags li:not(${techList[removeIndex]})`)
        .forEach((li, item)=>{
            li.classList.remove("inactive");
        });

        document.querySelector(skillList[skillIndex])
            .classList.add("enlarge");
        
        // highlight list of target tech and fade others
        document.querySelectorAll(`li${techList[skillIndex]}`)
        .forEach((li, item)=>{
            li.classList.add("highlight");
        });

        document.querySelectorAll(`.skills__tags li:not(${techList[skillIndex]})`)
        .forEach((li, item)=>{
            li.classList.add("inactive");
        });

        skillIndex++;
    } else {
        // reset
        skillIndex = 0;
    }
}, 5000);

/**
 * Projects Section Animation
 */

const projectCards = document.querySelectorAll('.projects__card');
projectCards.forEach((projectCard, index)=>{
    projectCard.addEventListener('click', (e)=>{
        // projects__img -> projects__body -> projects__card attribute 'target'
        var projectItemID = e.target.parentElement.parentElement.dataset.target;
        var projectItem = document.querySelector(projectItemID);
        projectItem.style.display = "flex";

        // do transition first before we hide overflow for body tag
        window.setTimeout(()=>{
            projectItem.classList.add("enter");
        }, 100);

        // set overflow to hidden for body tag to disable scrolling
        window.setTimeout(()=>{
            document.body.style.overflow = "hidden";
        }, 300);
    });
});

const projectItems = document.querySelectorAll('.project-item');
projectItems.forEach((projectItem, index) => {
    projectItem.style.display = "none";
});

const projectCloses = document.querySelectorAll('.project-close');
projectCloses.forEach((projectClose, index)=>{
    projectClose.addEventListener('click', (e)=>{
        e.preventDefault();
        // i -> project-close -> project-parent-container -> project-item
        var projectItem = e.target.parentElement.parentElement.parentElement;
        document.body.style.overflow = "auto";
        projectItem.classList.remove("enter");

        window.setTimeout(()=>{
            projectItem.style.display = "none";
        }, 300);

    });
});