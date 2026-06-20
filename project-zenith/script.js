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

    const startCounting = (sectionEl) => {
        const counters = sectionEl.querySelectorAll('.card h3, .list-item h3');
        counters.forEach(counterEl => {
            const originalText = counterEl.textContent;
            const match = originalText.match(/(\d+)/);
            if (match && !counterEl.classList.contains('counted')) {
                counterEl.classList.add('counted');
                const targetNum = parseInt(match[1], 10);
                const prefix = originalText.substring(0, match.index);
                const suffix = originalText.substring(match.index + match[1].length);
                
                const duration = 1500;
                const startTime = performance.now();
                
                const updateCounter = (now) => {
                    const progress = Math.min((now - startTime) / duration, 1);
                    const easeProgress = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
                    const currentNum = Math.floor(easeProgress * targetNum);
                    counterEl.textContent = prefix + currentNum + suffix;
                    
                    if (progress < 1) {
                        requestAnimationFrame(updateCounter);
                    } else {
                        counterEl.textContent = originalText;
                    }
                };
                requestAnimationFrame(updateCounter);
            }
        });
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
                startCounting(entry.target);
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.scroll-reveal').forEach(el => observer.observe(el));

    // Fallback: Ensure sections are revealed on scroll even if IntersectionObserver fails or lags
    const fallbackReveal = () => {
        const reveals = document.querySelectorAll('.scroll-reveal:not(.visible)');
        reveals.forEach(el => {
            const rect = el.getBoundingClientRect();
            const viewHeight = window.innerHeight || document.documentElement.clientHeight;
            if (rect.top <= viewHeight * 0.85) {
                const cards = el.querySelectorAll('.card, .list-item, .info-nav-card, .reward-card');
                cards.forEach((card, i) => {
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                });
                el.classList.add('visible');
                startCounting(el);
            }
        });
    };
    window.addEventListener('scroll', fallbackReveal, { passive: true });
    // Run once on load to show any already-visible items
    setTimeout(fallbackReveal, 400);

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
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                nav.classList.add('scrolled');
            } else {
                nav.classList.remove('scrolled');
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
        bgOverlay.style.transform = 'scale(1.15)';
        bgOverlay.style.transformOrigin = 'center';
        window.addEventListener('scroll', () => {
            const scrolled = window.scrollY;
            // Limit the parallax shift to -60px to prevent exposing black gaps on long pages
            const offset = Math.max(scrolled * -0.015, -60);
            bgOverlay.style.transform = `translate3d(0, ${offset}px, 0) scale(1.15)`;
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
    // ─── Custom Discord Widget Fetch ───
    const discordCountEl = document.getElementById('discord-online-count');
    if (discordCountEl) {
        // Fetch from Discord's widget API
        fetch('https://discord.com/api/guilds/1431859727285092403/widget.json')
            .then(res => res.json())
            .then(data => {
                if (data && data.presence_count) {
                    discordCountEl.textContent = data.presence_count;
                } else {
                    discordCountEl.textContent = '0';
                }
            })
            .catch(err => {
                console.error('Error fetching Discord data', err);
                discordCountEl.textContent = 'Offline';
            });
    }

});
