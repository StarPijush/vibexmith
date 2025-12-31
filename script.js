// ===== Scroll Reveal =====
const reveals = document.querySelectorAll(".reveal");

function handleReveal() {
  reveals.forEach(el => {
    const top = el.getBoundingClientRect().top;
    const windowHeight = window.innerHeight;

    if (top < windowHeight - 100) {
      el.classList.add("visible");
    }
  });
}

// ===== Parallax Hero =====
const hero = document.querySelector(".hero");

function handleParallax() {
  if (!hero) return;
  const scrollY = window.scrollY;
  hero.style.setProperty("--parallax", `${scrollY * 0.3}px`);
}

// ===== Parallax Sections =====
const parallaxLayers = document.querySelectorAll(".parallax-layer");

function handleSectionParallax() {
  parallaxLayers.forEach(layer => {
    const speed = 0.1; // subtle luxury speed
    const offset = window.scrollY * speed;
    layer.style.transform = `translateY(${offset}px)`;
  });
}

// ===== Unified Scroll Handler =====
function handleScroll() {
  handleReveal();
  handleParallax();
  handleSectionParallax();
}

// Attach a single scroll listener
window.addEventListener("scroll", handleScroll);

// Run once on load
handleScroll();

// REAL VIEWPORT HEIGHT FIX (Mobile + Desktop)
function setRealVH() {
  const vh = window.innerHeight * 0.01;
  document.documentElement.style.setProperty('--vh', `${vh}px`);
}

// run once
setRealVH();

// update on resize / orientation change
window.addEventListener('resize', setRealVH);
window.addEventListener('orientationchange', setRealVH);


