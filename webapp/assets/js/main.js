// assets/js/main.js

(function () {
    // ========== Mobile Navigation Toggle ==========
    const navToggle = document.querySelector('.nav-toggle');
    const navLinks = document.querySelector('.nav-links');

    if (navToggle && navLinks) {
        navToggle.addEventListener('click', function () {
            const isExpanded = navToggle.getAttribute('aria-expanded') === 'true';
            navToggle.setAttribute('aria-expanded', !isExpanded);
            navToggle.classList.toggle('active');
            navLinks.classList.toggle('active');
        });

        // Close menu when clicking on a link
        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                navToggle.setAttribute('aria-expanded', 'false');
                navToggle.classList.remove('active');
                navLinks.classList.remove('active');
            });
        });

        // Close menu when clicking outside
        document.addEventListener('click', function (e) {
            if (!navToggle.contains(e.target) && !navLinks.contains(e.target)) {
                navToggle.setAttribute('aria-expanded', 'false');
                navToggle.classList.remove('active');
                navLinks.classList.remove('active');
            }
        });
    }

    // HOME counts + featured content
    if (document.getElementById("articleCount")) {
        loadCountsAndFeatured();
    }

    // CHECK flow
    const toStep2 = document.getElementById("toStep2");
    const backTo1 = document.getElementById("backTo1");
    const getResult = document.getElementById("getResult");

    if (toStep2 && backTo1 && getResult) {
        const stepPill = document.getElementById("stepPill");
        const step1 = document.getElementById("step1");
        const step2 = document.getElementById("step2");

        toStep2.onclick = () => {
            step1.style.display = "none";
            step2.style.display = "block";
            stepPill.textContent = "Step 2 of 2";
        };

        backTo1.onclick = () => {
            step2.style.display = "none";
            step1.style.display = "block";
            stepPill.textContent = "Step 1 of 2";
        };

        getResult.onclick = () => {
            // Basic scoring demo (client-friendly). Replace with API later.
            const stress = clamp(num("stress"), 0, 10);
            const sleep = clamp(num("sleep"), 0, 12);
            const anxiety = clamp(num("anxiety"), 0, 10);
            const mood = clamp(num("mood"), 0, 10);

            const panic = checked("panic") ? 1 : 0;
            const burnout = checked("burnout") ? 1 : 0;
            const isolation = checked("isolation") ? 1 : 0;
            const appetite = checked("appetite") ? 1 : 0;

            // score: higher stress/anxiety + lower sleep/mood + symptoms
            let score = 0;
            score += stress * 1.2;
            score += anxiety * 1.3;
            score += (8 - Math.min(sleep, 8)) * 1.4;  // penalty if sleep < 8
            score += (6 - mood) * 1.1;               // penalty if mood < 6
            score += (panic + burnout + isolation + appetite) * 2.0;

            // normalize
            // rough thresholds
            let level = "Low";
            let note = "You seem stable — keep healthy routines.";
            if (score >= 18) { level = "Moderate"; note = "Some signs of strain — consider support and changes."; }
            if (score >= 28) { level = "High"; note = "Strong signs of distress — consider reaching out soon."; }

            renderResult(level, note);
        };
    }

    function renderResult(level, note) {
        const title = document.getElementById("resultTitle");
        const text = document.getElementById("resultText");
        const box = document.getElementById("resultBox");
        const lvl = document.getElementById("level");
        const nt = document.getElementById("note");

        const a = document.getElementById("stepA");
        const b = document.getElementById("stepB");
        const c = document.getElementById("stepC");

        if (!title || !text || !box) return;

        title.textContent = "Your result";
        lvl.textContent = level;
        nt.textContent = note;
        box.style.display = "block";

        if (level === "Low") {
            a.textContent = "Keep sleep consistent and take short breaks daily.";
            b.textContent = "Try 10 minutes of breathing or walking.";
            c.textContent = "Read one article about stress management.";
        } else if (level === "Moderate") {
            a.textContent = "Reduce overload: pick 1–2 tasks to pause this week.";
            b.textContent = "Talk to a friend or trusted person about how you feel.";
            c.textContent = "Explore resources — consider professional support if it continues.";
        } else {
            a.textContent = "If you feel unsafe, use crisis resources immediately.";
            b.textContent = "Reach out to a professional (counselor/therapist/doctor).";
            c.textContent = "Reduce isolation: message someone today and schedule support.";
        }

        text.textContent = "This summary is guidance only, not a diagnosis. If symptoms persist, consider professional help.";
    }

    // Helpers
    function num(id) { return parseFloat(document.getElementById(id)?.value || "0"); }
    function checked(id) { return !!document.getElementById(id)?.checked; }
    function clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }

    async function loadCountsAndFeatured() {
        try {
            const [articles, blogs] = await Promise.all([
                fetch("/assets/data/articles.json").then(r => r.json()),
                fetch("/assets/data/blogs.json").then(r => r.json())
            ]);

            const aCount = document.getElementById("articleCount");
            const bCount = document.getElementById("blogCount");
            if (aCount) aCount.textContent = articles.length;
            if (bCount) bCount.textContent = blogs.length;

            // Featured
            const featuredWrap = document.getElementById("featuredArticles");
            if (featuredWrap) {
                featuredWrap.innerHTML = articles.slice(0, 3).map(cardHtml).join("");
            }

            const blogWrap = document.getElementById("latestBlogs");
            if (blogWrap) {
                blogWrap.innerHTML = blogs.slice(0, 3).map(cardHtml).join("");
            }
        } catch (e) {
            // ignore silently for static hosting where json might not load
        }
    }

    function cardHtml(item) {
        return `
      <a class="card" href="${item.url || '#'}">
        <span class="pill">${item.tag || 'Read'}</span>
        <h3>${escapeHtml(item.title || 'Untitled')}</h3>
        <p>${escapeHtml(item.excerpt || '')}</p>
      </a>
    `;
    }

    function escapeHtml(str) {
        return String(str).replace(/[&<>"']/g, s => ({
            '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
        }[s]));
    }
})();
