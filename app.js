const NEWS_DATA_PATH = 'news-data.json';

function formatUpdateTime(value) {
  if (!value) return '未知';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;

  const yyyy = date.getFullYear();
  const mm = String(date.getMonth() + 1).padStart(2, '0');
  const dd = String(date.getDate()).padStart(2, '0');
  const hh = String(date.getHours()).padStart(2, '0');
  const min = String(date.getMinutes()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd} ${hh}:${min}`;
}

function getArticleUpdatedAt(item) {
  return item.updated_at || `${item.date}T08:00:00`;
}

function byPinnedThenDateDescThenId(a, b) {
  const aPinned = Boolean(a.is_featured);
  const bPinned = Boolean(b.is_featured);

  if (aPinned !== bPinned) return bPinned - aPinned;
  if (a.date !== b.date) return b.date.localeCompare(a.date);
  return b.id - a.id;
}

function getCategories(items) {
  return [...new Set(items.map((item) => item.category))];
}

function cardTemplate(item) {
  const updatedAt = formatUpdateTime(getArticleUpdatedAt(item));
  return `
    <article class="card">
      <p class="meta">${item.category} · ${item.date} · ${item.source_name}</p>
      <h3>${item.title}</h3>
      <p class="muted">${item.summary}</p>
      <p class="updated-time">更新时间：${updatedAt}</p>
      <p class="insight"><strong>机会：</strong>${item.opportunity}</p>
      <div class="card-actions">
        <a class="text-link" href="article.html?id=${item.id}">查看情报全文 →</a>
        <a class="btn btn-secondary" href="${item.source_url}" target="_blank" rel="noopener noreferrer">来源链接</a>
      </div>
    </article>
  `;
}

function initHome(news) {
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
  const heroTitle = document.getElementById('hero-title');
  const heroSummary = document.getElementById('hero-summary');

  const coreOpportunity = news[0];

  if (coreOpportunity) {
    if (heroLink) heroLink.href = `article.html?id=${coreOpportunity.id}`;
    if (heroTitle) heroTitle.textContent = coreOpportunity.title;
    if (heroSummary) heroSummary.textContent = coreOpportunity.opportunity;
  }
}

function initCategory(news) {
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

  const filtered =
    currentCategory === '全部' ? news : news.filter((item) => item.category === currentCategory);
  listEl.innerHTML = filtered.map(cardTemplate).join('');
}

function initArticle(news) {
  const detailEl = document.getElementById('article-detail');
  const relatedEl = document.getElementById('related-list');
  if (!detailEl || !relatedEl) return;

  const params = new URLSearchParams(window.location.search);
  const id = Number(params.get('id'));
  const article = news.find((item) => item.id === id) || news[0];

  if (!article) return;
  const updatedAt = formatUpdateTime(getArticleUpdatedAt(article));

  detailEl.innerHTML = `
    <p class="meta">${article.category} · ${article.date} · ${article.source_name}</p>
    <h1>${article.title}</h1>
    <p class="updated-time">更新时间：${updatedAt}</p>
    <a class="btn btn-secondary source-btn" href="${article.source_url}" target="_blank" rel="noopener noreferrer">来源链接</a>
    <p class="summary lead">${article.summary}</p>

    <section class="info-block info-important">
      <h2>为什么重要</h2>
      <p>${article.why_it_matters}</p>
    </section>

    <h2>机会研判</h2>
    <p>${article.opportunity}</p>

    <section class="info-block info-risk">
      <h2>主要风险</h2>
      <p>${article.risk}</p>
    </section>

    <h2>情报正文</h2>
    <p>${article.content}</p>

    <a class="text-link" href="category.html?category=${encodeURIComponent(article.category)}">查看同主题情报 →</a>
  `;

  const related = news
    .filter((item) => item.category === article.category && item.id !== article.id)
    .slice(0, 3);

  relatedEl.innerHTML = related.length
    ? related
        .map(
          (item) => `
      <a class="related-item" href="article.html?id=${item.id}">
        <strong>${item.title}</strong>
        <span class="muted">${item.date} · ${item.source_name}</span>
      </a>
    `,
        )
        .join('')
    : '<p class="muted">暂无更多同主题情报。</p>';
}

async function loadNews() {
  const response = await fetch(NEWS_DATA_PATH, { cache: 'no-store' });
  if (!response.ok) throw new Error('无法读取新闻数据文件');

  const data = await response.json();
  if (!Array.isArray(data)) throw new Error('新闻数据格式错误：应为数组');

  return data.sort(byPinnedThenDateDescThenId);
}

async function boot() {
  try {
    const news = await loadNews();
    initHome(news);
    initCategory(news);
    initArticle(news);
  } catch (error) {
    console.error(error);

    const targets = ['latest-news', 'category-nav', 'category-list', 'article-detail'];
    targets.forEach((id) => {
      const el = document.getElementById(id);
      if (el) el.innerHTML = '<p class="muted">数据加载失败，请检查 news-data.json。</p>';
    });
  }
}

boot();
