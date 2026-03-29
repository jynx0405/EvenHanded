document.addEventListener('DOMContentLoaded', () => {
    const API_BASE_URL = 'http://127.0.0.1:8000'; // Make sure this matches actual backend URL, mostly 8000 for FastAPI

    // UI Elements
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    const btnCompareUrls = document.getElementById('analyze-urls-btn');
    const btnAnalyzeTopic = document.getElementById('analyze-topic-btn');
    const loadingState = document.getElementById('loading-state');
    const errorState = document.getElementById('error-state');
    const errorMessage = document.getElementById('error-message');
    const resultsSection = document.getElementById('results-section');
    const markdownContent = document.getElementById('markdown-content');
    const articlesGrid = document.getElementById('articles-grid');

    // Tab Switching Logic
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // reset active states
            tabBtns.forEach(b => {
                b.classList.remove('bg-surface-container-lowest', 'text-primary', 'shadow-sm', 'active');
                b.classList.add('text-on-surface-variant');
            });
            tabContents.forEach(c => {
                c.classList.add('hidden');
                c.classList.remove('active');
            });

            // Set current tab as active
            btn.classList.add('bg-surface-container-lowest', 'text-primary', 'shadow-sm', 'active');
            btn.classList.remove('text-on-surface-variant');
            
            const targetId = btn.getAttribute('data-tab') + '-tab';
            const targetTab = document.getElementById(targetId);
            targetTab.classList.remove('hidden');
            targetTab.classList.add('active');
        });
    });

    // Handle Search Topic
    btnAnalyzeTopic.addEventListener('click', async () => {
        const topicInput = document.getElementById('topic-input').value.trim();
        if (!topicInput) {
            showError('Please enter a topic to analyze.');
            return;
        }

        await fetchAnalysis(`${API_BASE_URL}/compare-topic`, { topic: topicInput });
    });

    // Handle Compare URLs
    btnCompareUrls.addEventListener('click', async () => {
        const url1 = document.getElementById('url1-input').value.trim();
        const url2 = document.getElementById('url2-input').value.trim();
        if (!url1 || !url2) {
            showError('Please enter two valid URLs to compare.');
            return;
        }

        await fetchAnalysis(`${API_BASE_URL}/compare-urls`, { url1, url2 });
    });

    // Core Fetch Function
    async function fetchAnalysis(endpoint, payload) {
        showLoading();

        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                throw new Error(`Server returned status: ${response.status}`);
            }

            const data = await response.json();

            if (data.error) {
                throw new Error(data.error);
            }

            renderResults(data);
        } catch (err) {
            console.error('API Error:', err);
            showError(err.message || 'An unexpected error occurred connecting to the backend. Make sure the FastAPI server is running with CORS enabled.');
        }
    }

    // Render Data
    function renderResults(data) {
        hideLoading();
        resultsSection.style.display = 'block';

        // Render Markdown
        if (data.comparison) {
            markdownContent.innerHTML = marked.parse(data.comparison);
            markdownContent.classList.add('markdown-body', 'space-y-4');
        } else {
            markdownContent.innerHTML = '<p>No analysis generated.</p>';
        }

        // Render Article Cards
        articlesGrid.innerHTML = '';
        if (data.articles && Array.isArray(data.articles)) {
            data.articles.forEach(article => {
                articlesGrid.appendChild(createArticleCard(article));
            });
        }
    }

    // Create a single article card element matching Design System
    function createArticleCard(article) {
        const card = document.createElement('div');
        card.className = 'bg-surface-container-lowest p-6 rounded-[1.25rem] shadow-sm hover:shadow-md transition-all flex flex-col justify-between';

        const headline = article.headline || 'Untitled Article';
        const url = article.url || '#';
        const source = article.source || new URL(url).hostname;
        const features = article.features || {};

        const sentiment = features.sentiment !== undefined ? features.sentiment.toFixed(2) : 'N/A';
        const emotion = features.emotion || 'N/A';

        const renderTags = (items, colorClass) => {
            if (!items || !items.length) return '';
            return items.map(t => `<span class="${colorClass} text-[10px] px-2 py-1 rounded-full font-bold uppercase tracking-wider mb-1">${t}</span>`).join('');
        };

        const loadedTags = renderTags(features.loaded_words, 'bg-error-container text-on-error-container');
        const speculativeTags = renderTags(features.speculative_words, 'bg-tertiary-fixed text-on-tertiary-fixed');

        let sentimentColor = 'text-primary';
        if (features.sentiment > 0.1) sentimentColor = 'text-green-600 dark:text-green-400';
        if (features.sentiment < -0.1) sentimentColor = 'text-red-600 dark:text-red-400';

        card.innerHTML = `
            <div>
                <div class="flex justify-between items-center mb-4">
                    <span class="text-[10px] font-bold text-primary-container uppercase tracking-widest bg-surface-container-high px-2 py-1 rounded-lg">
                        ${source}
                    </span>
                    <span class="text-[11px] font-bold ${sentimentColor}">Sen: ${sentiment}</span>
                </div>
                <h3 class="font-headline font-bold text-lg mb-3 leading-snug line-clamp-3 text-primary group-hover:underline">
                    <a href="${url}" target="_blank" rel="noopener noreferrer">${headline}</a>
                </h3>
            </div>
            
            <div class="mt-4 pt-4 border-t border-surface-variant/30 text-sm">
                <div class="flex justify-between items-center mb-3">
                    <span class="text-on-surface-variant text-xs font-bold uppercase tracking-widest">Emotion</span>
                    <span class="font-semibold text-on-surface">${emotion}</span>
                </div>
                
                ${features.loaded_words && features.loaded_words.length ? `
                <div class="mb-3">
                    <span class="text-[10px] text-on-surface-variant uppercase font-bold tracking-widest block mb-2">Loaded Framing</span>
                    <div class="flex flex-wrap gap-1">${loadedTags}</div>
                </div>` : ''}

                ${features.speculative_words && features.speculative_words.length ? `
                <div class="mb-3">
                    <span class="text-[10px] text-on-surface-variant uppercase font-bold tracking-widest block mb-2">Speculative Elements</span>
                    <div class="flex flex-wrap gap-1">${speculativeTags}</div>
                </div>` : ''}
            </div>
        `;
        return card;
    }

    // State Management Helpers
    function showLoading() {
        loadingState.style.display = 'flex';
        errorState.style.display = 'none';
        resultsSection.style.display = 'none';

        // Scroll into view
        setTimeout(() => {
            loadingState.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 50);
    }

    function hideLoading() {
        loadingState.style.display = 'none';
    }

    function showError(msg) {
        hideLoading();
        errorState.style.display = 'flex';
        errorMessage.textContent = msg;
    }

    // Hide everything on initial load using standard styles just to be safe
    loadingState.style.display = 'none';
    errorState.style.display = 'none';
    resultsSection.style.display = 'none';
});
