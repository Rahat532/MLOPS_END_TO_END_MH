// assets/js/content.js
(async function () {
    // ARTICLES page
    if (document.getElementById("articleList")) {
        const data = await safeLoad("/assets/data/articles.json");
        mountList({
            data,
            listId: "articleList",
            searchId: "articleSearch",
            tagsId: "articleTags"
        });
    }

    // BLOG page
    if (document.getElementById("blogList")) {
        const data = await safeLoad("/assets/data/blogs.json");
        mountList({
            data,
            listId: "blogList",
            searchId: "blogSearch",
            tagsId: "blogTags"
        });
    }

    async function safeLoad(path) {
        try { return await fetch(path).then(r => r.json()); }
        catch (e) { return []; }
    }

    function mountList({ data, listId, searchId, tagsId }) {
        let activeTag = "All";
        const listEl = document.getElementById(listId);
        const searchEl = document.getElementById(searchId);
        const tagsEl = document.getElementById(tagsId);

        const tags = ["All", ...unique(data.map(x => x.tag).filter(Boolean))];
        tagsEl.innerHTML = tags.map(t => `<button class="tag ${t === "All" ? "active" : ""}" data-tag="${escapeHtml(t)}">${escapeHtml(t)}</button>`).join("");

        tagsEl.addEventListener("click", (e) => {
            const btn = e.target.closest(".tag");
            if (!btn) return;
            activeTag = btn.dataset.tag;
            [...tagsEl.querySelectorAll(".tag")].forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            render();
        });

        if (searchEl) searchEl.addEventListener("input", render);

        render();

        function render() {
            const q = (searchEl?.value || "").trim().toLowerCase();

            const filtered = data.filter(item => {
                const inTag = (activeTag === "All") || (String(item.tag || "") === activeTag);
                const text = `${item.title || ""} ${item.excerpt || ""} ${item.tag || ""}`.toLowerCase();
                const inSearch = !q || text.includes(q);
                return inTag && inSearch;
            });

            listEl.innerHTML = filtered.map(cardHtml).join("") || `
        <div class="card" style="grid-column: span 3;">
          <span class="pill">No results</span>
          <h3>Nothing found</h3>
          <p>Try another keyword or choose a different tag.</p>
        </div>
      `;
        }
    }

    function cardHtml(item) {
        return `
      <a class="card" href="${item.url || '#'}">
        <span class="pill">${escapeHtml(item.tag || 'Read')}</span>
        <h3>${escapeHtml(item.title || 'Untitled')}</h3>
        <p>${escapeHtml(item.excerpt || '')}</p>
      </a>
    `;
    }

    function unique(arr) { return [...new Set(arr)]; }

    function escapeHtml(str) {
        return String(str).replace(/[&<>"']/g, s => ({
            '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
        }[s]));
    }
})();
