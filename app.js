const news = window.newsItems || [];

function getCategories(items) {
  return [...new Set(items.map((item) => item.category))];
}

function cardTemplate(item) {
  return `
    <article class="card">
      <p class="meta">${item.category} · ${item.date}</p>
      <h3>${item.title}</h3>
      <p class="muted">${item.summary}</p>
      <a class="text-link" href="article.html?id=${item.id}">阅读全文 →</a>
    </article>
  `;
}

function initHome() {
  const latestEl = document.getElementById('latest-news');
  const categoryEl = document.getElementById('category-nav');
  if (!latestEl || !categoryEl) return;

  const latest = news.slice(0, 6);
  latestEl.innerHTML = latest.map(cardTemplate).join('');

  const categories = getCategories(news);
  categoryEl.innerHTML = categories
    .map(
      (category) => `
      <a class="category-box" href="category.html?category=${encodeURIComponent(category)}">
        <span>${category}</span>
      </a>
    `,
    )
    .join('');

  const heroLink = document.getElementById('hero-link');
  if (heroLink && news[0]) {
    heroLink.href = `article.html?id=${news[0].id}`;
  }
}

function initCategory() {
  const listEl = document.getElementById('category-list');
  const chipsEl = document.getElementById('category-chips');
  if (!listEl || !chipsEl) return;

  const params = new URLSearchParams(window.location.search);
  const currentCategory = params.get('category') || '全部';
  const categories = ['全部', ...getCategories(news)];

  chipsEl.innerHTML = categories
    .map((category) => {
      const active = category === currentCategory;
      const href =
        category === '全部'
          ? 'category.html'
          : `category.html?category=${encodeURIComponent(category)}`;
      return `<a class="chip ${active ? 'active' : ''}" href="${href}">${category}</a>`;
    })
    .join('');

  const filtered = currentCategory === '全部' ? news : news.filter((item) => item.category === currentCategory);
  listEl.innerHTML = filtered.map(cardTemplate).join('');
}

function initArticle() {
  const detailEl = document.getElementById('article-detail');
  const relatedEl = document.getElementById('related-list');
  if (!detailEl || !relatedEl) return;

  const params = new URLSearchParams(window.location.search);
  const id = Number(params.get('id'));
  const article = news.find((item) => item.id === id) || news[0];

  if (!article) return;

  detailEl.innerHTML = `
    <p class="meta">${article.category} · ${article.date}</p>
    <h1>${article.title}</h1>
    <p class="summary lead">${article.summary}</p>
    <h2>机会看点</h2>
    <p>${article.opportunity}</p>
    <h2>正文</h2>
    <p>${article.content}</p>
    <a class="text-link" href="category.html?category=${encodeURIComponent(article.category)}">查看同类资讯 →</a>
  `;

  const related = news.filter((item) => item.category === article.category && item.id !== article.id).slice(0, 3);
  relatedEl.innerHTML = related.length
    ? related
        .map(
          (item) => `
      <a class="related-item" href="article.html?id=${item.id}">
        <strong>${item.title}</strong>
        <span class="muted">${item.date}</span>
      </a>
    `,
        )
        .join('')
    : '<p class="muted">暂无更多同类文章。</p>';
}

initHome();
initCategory();
initArticle();
