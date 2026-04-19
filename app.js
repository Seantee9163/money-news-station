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

function getUniqueDates(items) {
  return [...new Set(items.map((item) => item.date))].sort((a, b) => b.localeCompare(a));
}

function cardTemplate(item) {
  const updatedAt = formatUpdateTime(getArticleUpdatedAt(item));
  const pinnedTag = item.is_featured ? '<span class="pin-tag">置顶新闻</span>' : '';
  return `
    <article class="card">
      <p class="meta">${item.category} · ${item.date} · ${item.source_name} ${pinnedTag}</p>
      <h3>${item.title}</h3>
      <p class="muted">${item.summary}</p>
      <p class="updated-time">更新时间：${updatedAt}</p>
      <div class="card-actions">
        <a class="text-link" href="article.html?id=${item.id}">查看情报全文 →</a>
      </div>
    </article>
  `;
}

function compactCardTemplate(item) {
  const updatedAt = formatUpdateTime(getArticleUpdatedAt(item));
  return `
    <article class="card compact-card">
      <h3>${item.title}</h3>
      <p class="muted">${item.summary}</p>
      <p class="updated-time">更新时间：${updatedAt}</p>
      <div class="card-actions">
        <a class="text-link" href="article.html?id=${item.id}">查看详情 →</a>
      </div>
    </article>
  `;
}

function getDateFilterValue(inputEl) {
  if (!inputEl || !inputEl.value) return '';
  return inputEl.value;
}

function initHome(news) {
  const latestEl = document.getElementById('latest-news');
  const categoryEl = document.getElementById('category-nav');
  if (!latestEl || !categoryEl) return;

  const today = new Date().toISOString().slice(0, 10);
  const todayNews = news.filter((item) => item.date === today);
  const toggleBtn = document.getElementById('today-filter-toggle');
  const feedLabel = document.getElementById('news-feed-label');
  const dateInput = document.getElementById('home-date-filter');
  const clearDateBtn = document.getElementById('clear-home-date-filter');

  const params = new URLSearchParams(window.location.search);
  let onlyToday = params.get('today') === '1';

  function renderNewsList() {
    const selectedDate = getDateFilterValue(dateInput);
    let source = onlyToday ? todayNews : news;

    if (selectedDate) {
      source = source.filter((item) => item.date === selectedDate);
    }

    const latest = source.slice(0, 6);
    latestEl.innerHTML = latest.length
      ? latest.map(compactCardTemplate).join('')
      : '<p class="muted">当前筛选条件下暂无情报，请尝试清空日期或切换查看范围。</p>';

    if (feedLabel) {
      const scopeText = onlyToday ? '仅显示今日更新' : '显示全部情报';
      feedLabel.textContent = selectedDate ? `${scopeText} · 日期：${selectedDate}` : scopeText;
    }

    if (toggleBtn) toggleBtn.textContent = onlyToday ? '查看全部情报' : '只看今日更新';
  }

  renderNewsList();

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
  const todayUpdateDateEl = document.getElementById('today-update-date');
  const todayCountEl = document.getElementById('today-count');
  const pinnedCountEl = document.getElementById('pinned-count');
  const categoryCountEl = document.getElementById('category-count');

  const coreOpportunity = news[0];

  if (coreOpportunity) {
    if (heroLink) heroLink.href = `article.html?id=${coreOpportunity.id}`;
    if (heroTitle) heroTitle.textContent = coreOpportunity.title;
    if (heroSummary) heroSummary.textContent = coreOpportunity.opportunity;
  }

  if (todayUpdateDateEl) todayUpdateDateEl.textContent = today;
  if (todayCountEl) todayCountEl.textContent = String(todayNews.length);
  if (pinnedCountEl) pinnedCountEl.textContent = String(news.filter((item) => item.is_featured).length);
  if (categoryCountEl) categoryCountEl.textContent = String(categories.length);

  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      onlyToday = !onlyToday;
      renderNewsList();
      latestEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  }

  if (dateInput) {
    dateInput.addEventListener('change', renderNewsList);
  }

  if (clearDateBtn && dateInput) {
    clearDateBtn.addEventListener('click', () => {
      dateInput.value = '';
      renderNewsList();
    });
  }
}

function initCategory(news) {
  const listEl = document.getElementById('category-list');
  const chipsEl = document.getElementById('category-chips');
  const dateInput = document.getElementById('category-date-filter');
  const clearDateBtn = document.getElementById('clear-category-date-filter');
  const dateHint = document.getElementById('category-date-hint');

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

  function renderCategoryList() {
    const selectedDate = getDateFilterValue(dateInput);
    let filtered =
      currentCategory === '全部' ? news : news.filter((item) => item.category === currentCategory);

    if (selectedDate) {
      filtered = filtered.filter((item) => item.date === selectedDate);
    }

    listEl.innerHTML = filtered.length
      ? filtered.map(cardTemplate).join('')
      : '<p class="muted">该分类在当前日期下暂无情报。</p>';

    if (dateHint) {
      dateHint.textContent = selectedDate ? `当前日期筛选：${selectedDate}` : '未设置日期筛选';
    }
  }

  renderCategoryList();

  if (dateInput) dateInput.addEventListener('change', renderCategoryList);
  if (clearDateBtn && dateInput) {
    clearDateBtn.addEventListener('click', () => {
      dateInput.value = '';
      renderCategoryList();
    });
  }
}

function initArchive(news) {
  const archiveListEl = document.getElementById('archive-list');
  const archiveDatesEl = document.getElementById('archive-dates');
  const archiveDateInput = document.getElementById('archive-date-filter');
  const archiveDateCountEl = document.getElementById('archive-date-count');

  if (!archiveListEl || !archiveDatesEl || !archiveDateInput) return;

  const uniqueDates = getUniqueDates(news);

  archiveDatesEl.innerHTML = uniqueDates
    .map((date) => `<button type="button" class="chip archive-date-chip" data-date="${date}">${date}</button>`)
    .join('');

  function renderArchive() {
    const selectedDate = getDateFilterValue(archiveDateInput);
    const datesToRender = selectedDate ? [selectedDate] : uniqueDates;

    const html = datesToRender
      .map((date) => {
        const articles = news.filter((item) => item.date === date);
        if (!articles.length) return '';

        return `
          <section class="archive-day section-card">
            <div class="archive-day-head">
              <h2>${date}</h2>
              <span class="inline-hint">共 ${articles.length} 条</span>
            </div>
            <div class="grid cols-2">
              ${articles.map(cardTemplate).join('')}
            </div>
          </section>
        `;
      })
      .join('');

    archiveListEl.innerHTML = html || '<p class="muted">该日期暂无新闻归档。</p>';

    if (archiveDateCountEl) {
      const count = selectedDate ? news.filter((item) => item.date === selectedDate).length : news.length;
      archiveDateCountEl.textContent = selectedDate
        ? `已筛选 ${selectedDate}（${count} 条）`
        : `当前共归档 ${news.length} 条`;
    }

    archiveDatesEl.querySelectorAll('.archive-date-chip').forEach((chip) => {
      const active = chip.dataset.date === selectedDate;
      chip.classList.toggle('active', active);
    });
  }

  archiveDatesEl.addEventListener('click', (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) return;
    if (!target.classList.contains('archive-date-chip')) return;

    const nextDate = target.dataset.date || '';
    archiveDateInput.value = nextDate;
    renderArchive();
  });

  archiveDateInput.addEventListener('change', renderArchive);
  renderArchive();
}

function initArticle(news) {
  const detailEl = document.getElementById('article-detail');
  const relatedEl = document.getElementById('related-list');
  if (!detailEl || !relatedEl) return;

  const params = new URLSearchParams(window.location.search);
  const id = Number(params.get('id'));
  const article = news.find((item) => item.id === id) || news[0];

  if (!article) return;
  const currentIndex = news.findIndex((item) => item.id === article.id);
  const prevArticle = currentIndex > 0 ? news[currentIndex - 1] : null;
  const nextArticle = currentIndex < news.length - 1 ? news[currentIndex + 1] : null;
  const updatedAt = formatUpdateTime(getArticleUpdatedAt(article));
  const whyImportantText = article.why_it_matters || '该情报的重要性暂未补充，请结合正文与机会研判综合判断。';
  const riskText = article.risk || '暂无明确风险提示，建议结合后续数据持续跟踪。';
  const sourceName = article.source_name || '未提供';
  const sourceUrl = article.source_url || '';

  detailEl.innerHTML = `
    <div class="article-toolbar">
      <a class="btn btn-secondary" href="index.html?today=1">← 返回今日情报</a>
    </div>
    <p class="meta">${article.category} · ${article.date}</p>
    <h1>${article.title}</h1>
    <p class="updated-time">更新时间：${updatedAt}</p>
    <p class="summary lead">${article.summary}</p>

    <section class="info-block info-source">
      <h2>来源信息</h2>
      <p><strong>source_name：</strong>${sourceName}</p>
      <p><strong>source_url：</strong>${sourceUrl ? `<a href="${sourceUrl}" target="_blank" rel="noopener noreferrer">${sourceUrl}</a>` : '未提供'}</p>
    </section>

    <section class="info-block info-important">
      <h2>why_it_matters</h2>
      <p>${whyImportantText}</p>
    </section>

    <h2>机会研判</h2>
    <p>${article.opportunity}</p>

    <section class="info-block info-risk">
      <h2>risk</h2>
      <p>${riskText}</p>
    </section>

    <h2>情报正文</h2>
    <p>${article.content}</p>

    <div class="article-footer-links">
      <a class="text-link" href="category.html?category=${encodeURIComponent(article.category)}">查看同主题情报 →</a>
    </div>
    <nav class="pager-nav" aria-label="文章翻页">
      ${
        prevArticle
          ? `<a class="pager-link" href="article.html?id=${prevArticle.id}">← 上一篇<br /><span>${prevArticle.title}</span></a>`
          : '<span class="pager-link disabled">← 上一篇<br /><span>已是第一篇</span></span>'
      }
      ${
        nextArticle
          ? `<a class="pager-link" href="article.html?id=${nextArticle.id}">下一篇 →<br /><span>${nextArticle.title}</span></a>`
          : '<span class="pager-link disabled">下一篇 →<br /><span>已是最后一篇</span></span>'
      }
    </nav>
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
    initArchive(news);
    initArticle(news);
  } catch (error) {
    console.error(error);

    const targets = ['latest-news', 'category-nav', 'category-list', 'archive-list', 'article-detail'];
    targets.forEach((id) => {
      const el = document.getElementById(id);
      if (el) el.innerHTML = '<p class="muted">数据加载失败，请检查 news-data.json。</p>';
    });
  }
}

boot();
