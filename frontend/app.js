// Базовый URL API: тот же хост, что и страница (обязательно открывать http://127.0.0.1:8000/)
const API = (typeof window !== 'undefined' && window.location.origin && window.location.protocol !== 'file:')
  ? window.location.origin
  : 'http://127.0.0.1:8000';
function show(el, on) { el.style.display = on ? 'block' : 'none'; }
function showResult(text) {
  show(document.getElementById('loading'), false);
  const r = document.getElementById('result');
  const e = document.getElementById('error');
  r.textContent = text;
  r.style.display = 'block';
  e.style.display = 'none';
}
function showError(msg) {
  show(document.getElementById('loading'), false);
  document.getElementById('result').style.display = 'none';
  const e = document.getElementById('error');
  e.textContent = msg;
  e.style.display = 'block';
}
function formatAnalysis(analysis) {
  if (!analysis) return '';
  let s = '';
  if (analysis.summary) s += 'Резюме: ' + analysis.summary + '\n\n';
  if (analysis.strengths?.length) s += 'Сильные стороны:\n' + analysis.strengths.map(x => '• ' + x).join('\n') + '\n\n';
  if (analysis.weaknesses?.length) s += 'Слабые стороны:\n' + analysis.weaknesses.map(x => '• ' + x).join('\n') + '\n\n';
  if (analysis.unique_offers?.length) s += 'Уникальные предложения:\n' + analysis.unique_offers.map(x => '• ' + x).join('\n') + '\n\n';
  if (analysis.recommendations?.length) s += 'Рекомендации:\n' + analysis.recommendations.map(x => '• ' + x).join('\n') + '\n\n';
  if (analysis.news_highlights?.length) s += 'Что нового:\n' + analysis.news_highlights.map(x => '• ' + x).join('\n') + '\n\n';
  if (analysis.attention_points?.length) s += 'На что обратить внимание:\n' + analysis.attention_points.map(x => '• ' + x).join('\n') + '\n\n';
  if (analysis.key_topics?.length) s += 'Ключевые темы:\n' + analysis.key_topics.map(x => '• ' + x).join('\n') + '\n\n';
  if (analysis.description) s += 'Описание: ' + analysis.description + '\n\n';
  if (analysis.marketing_insights?.length) s += 'Инсайты:\n' + analysis.marketing_insights.map(x => '• ' + x).join('\n') + '\n\n';
  if (analysis.visual_style_score != null) s += 'Оценка визуального стиля: ' + analysis.visual_style_score + '/10\n';
  if (analysis.visual_style_analysis) s += analysis.visual_style_analysis + '\n\n';
  return s || JSON.stringify(analysis, null, 2);
}

document.querySelectorAll('.tab').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('panel-' + btn.dataset.tab).classList.add('active');
    document.getElementById('result').style.display = 'none';
    document.getElementById('error').style.display = 'none';
    if (btn.dataset.tab === 'history') loadHistory();
  });
});

document.getElementById('btn-analyze-text').addEventListener('click', async () => {
  const text = document.getElementById('text-input').value.trim();
  if (text.length < 10) { showError('Введите минимум 10 символов'); return; }
  show(document.getElementById('loading'), true);
  try {
    const url = API + '/analyze_text';
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    let data = {};
    try { data = await res.json(); } catch (_) {}
    if (!res.ok) {
      showError(res.status === 404
        ? `Сервер вернул 404. Убедитесь, что сервер запущен (python run.py) и откройте http://127.0.0.1:8000`
        : (data.detail || data.error || `Ошибка ${res.status}`));
      return;
    }
    if (data.success) showResult(formatAnalysis(data.analysis));
    else showError(data.error || 'Ошибка анализа');
  } catch (err) { showError(err.message || 'Ошибка сети'); }
});

document.getElementById('btn-analyze-image').addEventListener('click', async () => {
  const input = document.getElementById('image-input');
  if (!input.files?.length) { showError('Выберите файл изображения'); return; }
  show(document.getElementById('loading'), true);
  const form = new FormData();
  form.append('file', input.files[0]);
  try {
    const res = await fetch(API + '/analyze_image', { method: 'POST', body: form });
    const data = await res.json();
    if (data.success) showResult(formatAnalysis(data.analysis));
    else showError(data.error || 'Ошибка анализа');
  } catch (err) { showError(err.message); }
});

document.getElementById('btn-parse').addEventListener('click', async () => {
  const url = document.getElementById('parse-input').value.trim();
  if (!url) { showError('Введите URL'); return; }
  show(document.getElementById('loading'), true);
  try {
    const res = await fetch(API + '/parse_demo', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    });
    const data = await res.json();
    if (data.success && data.data) {
      const d = data.data;
      let s = 'URL: ' + d.url + '\n';
      if (d.title) s += 'Title: ' + d.title + '\n';
      if (d.h1) s += 'H1: ' + d.h1 + '\n';
      if (d.analysis) s += '\n' + formatAnalysis(d.analysis);
      showResult(s);
    } else showError(data.error || 'Ошибка парсинга');
  } catch (err) { showError(err.message); }
});

function formatHistoryDetails(item) {
  if (!item || !item.details) return '';
  const d = item.details;
  if (item.request_type === 'parse') {
    let s = 'URL: ' + (d.url || '') + '\n';
    if (d.title) s += 'Title: ' + d.title + '\n';
    if (d.h1) s += 'H1: ' + d.h1 + '\n';
    if (d.first_paragraph) s += 'Первый абзац: ' + (d.first_paragraph || '').slice(0, 300) + (d.first_paragraph && d.first_paragraph.length > 300 ? '…' : '') + '\n\n';
    if (d.analysis) s += formatAnalysis(d.analysis);
    return s;
  }
  if (d.analysis) return formatAnalysis(d.analysis);
  return JSON.stringify(d, null, 2);
}

let historyItems = [];

function loadHistory() {
  fetch(API + '/history')
    .then(r => r.json())
    .then(data => {
      historyItems = data.items || [];
      const list = document.getElementById('history-list');
      list.innerHTML = '';
      historyItems.forEach((item, index) => {
        const div = document.createElement('div');
        div.className = 'history-item';
        div.dataset.index = index;
        const hasDetails = item.details && (item.request_type === 'parse' || item.details.analysis);
        div.innerHTML = '<span class="type">' + item.request_type + '</span> ' + (item.timestamp || '').slice(0, 19) + '<br>' + (item.request_summary || '').slice(0, 80) + (item.request_summary && item.request_summary.length > 80 ? '…' : '') + '<br><span class="time">' + (item.response_summary || '').slice(0, 100) + '</span>' + (hasDetails ? '<br><span class="open-hint">Клик — открыть полную информацию</span>' : '');
        if (hasDetails) {
          div.style.cursor = 'pointer';
          div.addEventListener('click', () => {
            document.getElementById('error').style.display = 'none';
            showResult(formatHistoryDetails(item));
          });
        }
        list.appendChild(div);
      });
    })
    .catch(() => {});
}

document.getElementById('btn-clear-history').addEventListener('click', async () => {
  try {
    await fetch(API + '/history', { method: 'DELETE' });
    loadHistory();
    showResult('История очищена.');
  } catch (err) { showError(err.message); }
});
