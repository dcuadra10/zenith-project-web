// ═══════════════════════════════════════════════
// PROJECT ZENITH — Premium Interactions v2.0
// ═══════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {

    // ─── Scroll Reveal with Stagger ───
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                // Stagger cards within the section
                const cards = entry.target.querySelectorAll('.card, .list-item, .info-nav-card, .reward-card');
                cards.forEach((card, i) => {
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(30px)';
                    card.style.transition = `all 0.6s cubic-bezier(0.16, 1, 0.3, 1) ${i * 0.1}s`;
                    requestAnimationFrame(() => {
                        card.style.opacity = '1';
                        card.style.transform = 'translateY(0)';
                    });
                });
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.scroll-reveal').forEach(el => observer.observe(el));

    // ─── Mobile Navigation ───
    const menuToggle = document.querySelector('.menu-toggle');
    const navMenu = document.querySelector('nav ul');

    if (menuToggle && navMenu) {
        menuToggle.addEventListener('click', () => {
            menuToggle.classList.toggle('active');
            navMenu.classList.toggle('active');
            document.body.style.overflow = navMenu.classList.contains('active') ? 'hidden' : '';
        });

        document.querySelectorAll('nav ul li a').forEach(link => {
            link.addEventListener('click', () => {
                menuToggle.classList.remove('active');
                navMenu.classList.remove('active');
                document.body.style.overflow = '';
            });
        });
    }

    // ─── Smooth Scroll ───
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // ─── Nav Background on Scroll ───
    const nav = document.querySelector('nav');
    if (nav) {
        const isMobile = window.matchMedia('(max-width: 768px)').matches;
        const padScrolled = isMobile ? '12px 16px' : '14px 50px';
        const padDefault = isMobile ? '14px 16px' : '24px 50px';

        window.addEventListener('scroll', () => {
            const scrollY = window.scrollY;
            if (scrollY > 80) {
                nav.style.background = 'rgba(10, 10, 15, 0.85)';
                nav.style.borderBottom = '1px solid rgba(255, 215, 0, 0.06)';
                nav.style.padding = padScrolled;
            } else {
                nav.style.background = 'linear-gradient(to bottom, rgba(10, 10, 15, 0.6), transparent)';
                nav.style.borderBottom = 'none';
                nav.style.padding = padDefault;
            }
        }, { passive: true });
    }

    // ─── Detect touch device ───
    const isTouchDevice = ('ontouchstart' in window) || (navigator.maxTouchPoints > 0);
    const isDesktop = window.matchMedia('(min-width: 769px)').matches && !isTouchDevice;

    // ─── Card Tilt Effect (desktop non-touch only) ───
    if (isDesktop) {
        document.querySelectorAll('.card, .info-nav-card').forEach(card => {
            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;

                const rotateX = ((y - centerY) / centerY) * -3;
                const rotateY = ((x - centerX) / centerX) * 3;

                card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-8px) scale(1.01)`;
            });

            card.addEventListener('mouseleave', () => {
                card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateY(0) scale(1)';
                card.style.transition = 'all 0.5s cubic-bezier(0.16, 1, 0.3, 1)';
            });

            card.addEventListener('mouseenter', () => {
                card.style.transition = 'none';
            });
        });
    }

    // ─── Parallax Background ───
    const bgOverlay = document.querySelector('.background-overlay');
    if (bgOverlay && isDesktop) {
        window.addEventListener('scroll', () => {
            const scrolled = window.scrollY;
            // Subtle parallax that keeps the image center focus
            bgOverlay.style.transform = `translate3d(0, ${scrolled * 0.05}px, 0)`;
        }, { passive: true });
    }

    // ─── Typing Effect for Hero Stats ───
    const heroStats = document.querySelector('.hero-stats span');
    if (heroStats) {
        const text = heroStats.textContent;
        heroStats.textContent = '';
        heroStats.style.borderRight = '2px solid var(--gold-500)';
        let i = 0;
        const typeInterval = setInterval(() => {
            heroStats.textContent += text[i];
            i++;
            if (i >= text.length) {
                clearInterval(typeInterval);
                setTimeout(() => {
                    heroStats.style.borderRight = 'none';
                }, 1000);
            }
        }, 80);
    }
});
