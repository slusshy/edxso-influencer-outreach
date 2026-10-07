const byId = (id) => document.getElementById(id);
const state = { creators: [], runId: null, busy: false, toastTimer: null };
const starterPhrases = [
  'AI tools',
  'machine learning',
  'generative AI',
  'LLM tutorials',
  'AI automation',
  'Python AI',
];

const elements = {
  form: byId('campaign-form'),
  submit: byId('submit-button'),
  launch: byId('run-analysis-btn'),
  suggest: byId('suggest-queries'),
  target: byId('target'),
  targetDisplay: byId('target-display'),
  rows: byId('creator-rows'),
  table: byId('table-scroll'),
  empty: byId('empty-state'),
  resultCount: byId('result-count'),
  search: byId('filter-search'),
  status: byId('status-filter'),
  sort: byId('sort-filter'),
  history: byId('history-select'),
  export: byId('export-button'),
  dialog: byId('creator-dialog'),
  detail: byId('creator-detail'),
  toast: byId('toast'),
};

const setText = (id, value) => { byId(id).textContent = value; };

const showToast = (message) => {
  elements.toast.textContent = message;
  elements.toast.classList.add('visible');
  window.clearTimeout(state.toastTimer);
  state.toastTimer = window.setTimeout(() => elements.toast.classList.remove('visible'), 2600);
};

const formatNumber = (value) => {
  if (value === null || value === undefined || value === '') return '—';
  return Number(value).toLocaleString();
};

const formatPercent = (value) => {
  if (value === null || value === undefined || value === '') return '—';
  return `${Number(value).toFixed(2)}%`;
};

const make = (tag, className, text) => {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
};

const visibleCreators = () => {
  const query = elements.search.value.trim().toLocaleLowerCase();
  const status = elements.status.value;
  const sort = elements.sort.value;
  const list = state.creators.filter((creator) => {
    const matchesStatus = status === 'all' || creator.status === status;
    const haystack = [
      creator.channel_name,
      creator.category,
      creator.content_themes,
      creator.country,
      creator.contact_email,
    ].join(' ').toLocaleLowerCase();
    return matchesStatus && (!query || haystack.includes(query));
  });

  list.sort((left, right) => {
    if (sort === 'name') return (left.channel_name || '').localeCompare(right.channel_name || '');
    if (sort === 'engagement') return (right.engagement_rate ?? -1) - (left.engagement_rate ?? -1);
    return (right.subscribers ?? -1) - (left.subscribers ?? -1);
  });
  return list;
};

const createCell = (text, className) => {
  const cell = make('td', className);
  cell.textContent = text;
  return cell;
};

const addCopyButton = (label, text) => {
  const button = make('button', 'text-action', label);
  button.type = 'button';
  button.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(text || '');
      showToast(`${label.replace('Copy ', '')} copied`);
    } catch {
      showToast('Clipboard access is unavailable in this browser.');
    }
  });
  return button;
};

const showCreator = (creator) => {
  elements.detail.replaceChildren();
  const header = make('div', 'detail-header');
  const kicker = make('p', 'kicker', creator.category || 'CREATOR PROFILE');
  const title = make('h2', '', creator.channel_name || 'Creator');
  header.append(kicker, title);
  try {
    const profileUrl = new URL(creator.profile_url);
    if (profileUrl.protocol === 'https:' && ['www.youtube.com', 'youtube.com', 'm.youtube.com'].includes(profileUrl.hostname)) {
      const profile = make('a', 'detail-profile', 'Open YouTube profile ↗');
      profile.href = profileUrl.href;
      profile.target = '_blank';
      profile.rel = 'noopener noreferrer';
      header.append(profile);
    }
  } catch {
    // A missing or malformed profile URL should not create an unsafe link.
  }
  elements.detail.append(header);

  const facts = make('div', 'detail-facts');
  [
    ['Audience', formatNumber(creator.subscribers)],
    ['Engagement', formatPercent(creator.engagement_rate)],
    ['Average views', formatNumber(creator.avg_views)],
    ['Public email', creator.contact_email || 'Not found'],
  ].forEach(([label, value]) => {
    const fact = make('div', 'detail-fact');
    fact.append(make('small', '', label), make('strong', '', value));
    facts.append(fact);
  });
  elements.detail.append(facts);

  const sections = [
    ['Why this fit?', creator.filter_reason || 'No qualification notes available.'],
    ['Content themes', creator.content_themes || 'Not confidently identified'],
    ['Recent public videos', Array.isArray(creator.recent_content) && creator.recent_content.length
      ? creator.recent_content.join('\n')
      : 'No recent video titles were available.'],
    ['Personalization status', [
      creator.personalization_status || 'Not requested',
      creator.message_validation_errors || '',
    ].filter(Boolean).join(' — ')],
    ['Email draft', creator.email_pitch || 'No personalized draft generated.'],
    ['Instagram DM draft', creator.instagram_dm || 'No personalized draft generated.'],
  ];
  sections.forEach(([heading, body]) => {
    const section = make('section', 'detail-section');
    section.append(make('h3', '', heading), make('p', '', body));
    if (heading === 'Email draft' && creator.email_pitch) {
      section.append(addCopyButton('Copy email', creator.email_pitch));
    }
    if (heading === 'Instagram DM draft' && creator.instagram_dm) {
      section.append(addCopyButton('Copy DM', creator.instagram_dm));
    }
    elements.detail.append(section);
  });
  elements.dialog.showModal();
};

const renderRows = () => {
  const creators = visibleCreators();
  elements.rows.replaceChildren();
  elements.resultCount.textContent = `${creators.length}`;
  elements.table.classList.toggle('hidden', creators.length === 0);
  elements.empty.classList.toggle('hidden', creators.length !== 0);
  if (state.creators.length && !creators.length) {
    elements.empty.querySelector('h3').textContent = 'No creators match these filters.';
    elements.empty.querySelector('p').textContent = 'Clear the search text or choose a different fit filter to see more profiles.';
  } else if (!state.creators.length) {
    elements.empty.querySelector('h3').textContent = 'Your research starts here.';
    elements.empty.querySelector('p').textContent = 'Set a brief and search phrases above, then build a shortlist. Your results will be saved as a campaign snapshot.';
  }

  creators.forEach((creator) => {
    const row = make('tr');
    const nameCell = make('td', 'creator-name-cell');
    const name = make('strong', '', creator.channel_name || 'Unnamed creator');
    const meta = make('small', '', `${creator.country || 'Country unknown'} · ${creator.content_themes || 'Topic unclassified'}`);
    nameCell.append(name, meta);
    row.append(nameCell);

    const statusCell = make('td');
    const status = make('span', `fit-tag ${creator.status === 'Qualified' ? 'fit-good' : 'fit-review'}`, creator.status === 'Qualified' ? 'Good fit' : 'Review');
    statusCell.append(status);
    row.append(statusCell);
    row.append(createCell(formatNumber(creator.subscribers), 'numeric-cell'));
    row.append(createCell(formatPercent(creator.engagement_rate), 'numeric-cell'));
    row.append(createCell(creator.contact_email && creator.contact_email !== 'Not Found' ? creator.contact_email : 'Not found', 'email-cell'));

    const contactCell = make('td', 'contact-cell');
    const outreachStatus = creator.send_status || 'Draft only';
    contactCell.append(make('span', 'log-tag', outreachStatus));
    row.append(contactCell);

    const actionCell = make('td', 'row-action-cell');
    const details = make('button', 'row-action', 'Details ↗');
    details.type = 'button';
    details.addEventListener('click', () => showCreator(creator));
    actionCell.append(details);
    row.append(actionCell);
    elements.rows.append(row);
  });
};

const renderSummary = (summary, creators) => {
  const discovered = summary.discovered ?? creators.length;
  const qualified = summary.qualified ?? creators.filter((creator) => creator.status === 'Qualified').length;
  const emailCount = creators.filter((creator) => creator.contact_email && creator.contact_email !== 'Not Found').length;
  const rates = creators.map((creator) => creator.engagement_rate).filter((value) => typeof value === 'number');
  const average = rates.length ? rates.reduce((total, value) => total + value, 0) / rates.length : null;

  setText('stat-discovered', formatNumber(discovered));
  setText('stat-qualified', formatNumber(qualified));
  setText('stat-emails', formatNumber(emailCount));
  setText('stat-engagement', formatPercent(average));
  setText('qualified-note', `${discovered ? Math.round((qualified / discovered) * 100) : 0}% of creators found`);
  setText('chart-qualified', formatNumber(qualified));
  setText('chart-rejected', formatNumber(Math.max(0, discovered - qualified)));
  setText('fit-total', `${discovered} PROFILES`);
  byId('qualified-bar').style.width = `${discovered ? (qualified / discovered) * 100 : 0}%`;
  setText('research-note', discovered
    ? `${qualified} of ${discovered} profiles met the current fit criteria (${formatNumber(summary.min_subs)}–${formatNumber(summary.max_subs)} subscribers; at least ${formatPercent(summary.min_engagement)} engagement). ${emailCount} have a publicly listed email. Phrases: ${(summary.search_phrases || []).join(', ')}. Review each profile before reaching out.`
    : 'No profiles matched those search phrases. Try broader topics or a smaller audience minimum.');
};

const loadHistory = async (selectedRunId = '') => {
  const response = await fetch('/api/history');
  if (!response.ok) throw new Error('Campaign history could not be loaded.');
  const data = await response.json();
  const currentValue = selectedRunId || elements.history.value;
  elements.history.replaceChildren(new Option('Latest research', ''));
  (data.campaigns || []).forEach((campaign) => {
    const date = new Date(campaign.created_at).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' });
    const brief = campaign.campaign.length > 48 ? `${campaign.campaign.slice(0, 48)}…` : campaign.campaign;
    const option = new Option(`${date} · ${brief}`, campaign.id);
    elements.history.add(option);
  });
  if (currentValue && [...elements.history.options].some((option) => option.value === currentValue)) {
    elements.history.value = currentValue;
  } else {
    elements.history.value = '';
  }
  if (!currentValue && data.campaigns?.length) {
    const latest = data.campaigns[0];
    const snapshotResponse = await fetch(`/api/history/${encodeURIComponent(latest.id)}`);
    if (snapshotResponse.ok) {
      displayCampaign(await snapshotResponse.json(), latest.id);
      elements.history.value = latest.id;
    }
  }
};

const displayCampaign = (result, runId) => {
  const summary = result.summary || {};
  state.creators = Array.isArray(result.creators) ? result.creators : [];
  state.runId = runId || result.run_id || null;
  setText('campaign-title', summary.campaign || 'Latest research');
  renderSummary(summary, state.creators);
  renderRows();
  elements.export.disabled = !state.runId;
  elements.export.onclick = () => {
    if (state.runId) window.location.assign(`/api/history/${encodeURIComponent(state.runId)}/export.csv`);
  };
  byId('connection-state').innerHTML = '<i></i> Research saved';
  byId('connection-state').classList.add('connected');
};

const runCampaign = async (event) => {
  event?.preventDefault();
  if (state.busy) return;

  const minSubs = Number(byId('min-subs').value);
  const maxSubs = Number(byId('max-subs').value);
  const target = Number(elements.target.value);
  const campaign = byId('campaign').value.trim();
  const queries = byId('queries').value.split(',').map((query) => query.trim()).filter(Boolean);
  if (!campaign) return showToast('Add a campaign brief to continue.');
  if (minSubs > maxSubs) return showToast('Minimum audience must not exceed maximum audience.');
  if (!queries.length) return showToast('Add at least one search phrase.');

  state.busy = true;
  elements.submit.disabled = true;
  elements.launch.disabled = true;
  elements.submit.textContent = 'Researching creators…';
  byId('connection-state').innerHTML = '<i></i> Gathering public signals';
  byId('connection-state').classList.remove('connected');
  elements.empty.classList.remove('hidden');
  elements.empty.querySelector('h3').textContent = 'Looking for your next good fit.';
  elements.empty.querySelector('p').textContent = 'Searching YouTube, checking recent public videos and scoring creator relevance. Keep this tab open.';
  try {
    const response = await fetch('/api/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        target,
        campaign,
        queries,
        min_subs: minSubs,
        max_subs: maxSubs,
        min_engagement: Number(byId('min-engagement').value),
        personalize: byId('personalize').checked,
        review_log: byId('review-log').checked,
      }),
    });
    const result = await response.json();
    if (!response.ok || !result.success) throw new Error(result.error || `Research failed (${response.status}).`);
    displayCampaign(result, result.run_id);
    await loadHistory(result.run_id);
    showToast('Shortlist saved to campaign history.');
  } catch (error) {
    byId('connection-state').innerHTML = '<i></i> Research paused';
    byId('connection-state').classList.remove('connected');
    showToast(error.message || 'Could not complete the research.');
    if (!state.creators.length) {
      elements.empty.querySelector('h3').textContent = 'Research could not be completed.';
      elements.empty.querySelector('p').textContent = error.message || 'Check the server logs and API credentials, then try again.';
    }
  } finally {
    state.busy = false;
    elements.submit.disabled = false;
    elements.launch.disabled = false;
    elements.submit.innerHTML = 'Build my shortlist <span>→</span>';
  }
};

const suggestSearchPhrases = async () => {
  const campaign = byId('campaign').value.trim();
  if (!campaign) return showToast('Describe your product and intended audience first.');

  elements.suggest.disabled = true;
  elements.suggest.textContent = 'Thinking…';
  try {
    const response = await fetch('/api/suggest-searches', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ campaign }),
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Could not suggest search phrases.');
    const existing = byId('queries').value.split(',').map((item) => item.trim()).filter(Boolean);
    const isStarterList = existing.length === starterPhrases.length
      && starterPhrases.every((phrase, index) => phrase.toLocaleLowerCase() === existing[index].toLocaleLowerCase());
    const base = isStarterList ? [] : existing;
    const combined = [...new Map(
      [...base, ...result.queries].map((phrase) => [phrase.toLocaleLowerCase(), phrase]),
    ).values()].slice(0, 10);
    byId('queries').value = combined.join(', ');
    showToast('Relevant creator search phrases added. Review or edit them before searching.');
  } catch (error) {
    showToast(error.message || 'Search phrase suggestions are unavailable.');
  } finally {
    elements.suggest.disabled = false;
    elements.suggest.textContent = 'Suggest with Gemini ↗';
  }
};

elements.form.addEventListener('submit', runCampaign);
elements.launch.addEventListener('click', runCampaign);
elements.suggest.addEventListener('click', suggestSearchPhrases);
elements.target.addEventListener('input', () => { elements.targetDisplay.textContent = elements.target.value; });
[elements.search, elements.status, elements.sort].forEach((element) => element.addEventListener('input', renderRows));

elements.history.addEventListener('change', async () => {
  const runId = elements.history.value;
  if (!runId) {
    state.creators = [];
    state.runId = null;
    elements.export.disabled = true;
    setText('campaign-title', 'Latest research');
    setText('result-count', '0');
    setText('stat-discovered', '—');
    setText('stat-qualified', '—');
    setText('stat-emails', '—');
    setText('stat-engagement', '—');
    elements.rows.replaceChildren();
    elements.table.classList.add('hidden');
    elements.empty.classList.remove('hidden');
    return;
  }
  try {
    const response = await fetch(`/api/history/${encodeURIComponent(runId)}`);
    if (!response.ok) throw new Error('That campaign snapshot could not be opened.');
    const result = await response.json();
    displayCampaign(result, runId);
  } catch (error) {
    showToast(error.message);
  }
});

byId('history-nav').addEventListener('click', () => {
  elements.history.focus();
  elements.history.scrollIntoView({ behavior: 'smooth', block: 'center' });
});

byId('theme-toggle').addEventListener('click', () => {
  const dark = document.documentElement.dataset.theme !== 'dark';
  document.documentElement.dataset.theme = dark ? 'dark' : 'light';
  localStorage.setItem('fieldnotes-theme', dark ? 'dark' : 'light');
});

const savedTheme = localStorage.getItem('fieldnotes-theme');
document.documentElement.dataset.theme = savedTheme === 'dark' ? 'dark' : 'light';
elements.empty.querySelector('h3').textContent = 'Your research starts here.';
loadHistory().catch(() => showToast('Campaign history is temporarily unavailable.'));
