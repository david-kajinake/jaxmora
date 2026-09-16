console.log("Hello serch");
document.addEventListener('DOMContentLoaded', () => {
  const searchForm = document.getElementById('global-search-form');
  const searchInput = document.getElementById('search-input');
  const mainContent = document.getElementById('main-content');
  const searchResultsContent = document.getElementById('search-results-content');
  const searchResultsGrid = document.getElementById('search-results-grid');
  const searchTermDisplay = document.getElementById('search-term-display');
  const clearSearchBtn = document.getElementById('clear-search-btn');

  // Determine context globally from Django
  const pageContext = window.CATALOG_TYPE;

  if (!searchForm) return;

  searchForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = searchInput.value.trim();
    if (!query) return;

    mainContent.hidden = true;
    searchResultsContent.hidden = false;
    searchTermDisplay.textContent = query;
    searchResultsGrid.innerHTML = '<p class="loading-text">Searching JAXMORA...</p>';

    try {
      const response = await apiRequest(`/api/search/${encodeURIComponent(query)}/`);
      if (!response.ok) throw new Error('Search failed');
      const data = await response.json();

      renderContextualResults(data, pageContext);
    } catch (error) {
      searchResultsGrid.innerHTML = `<p class="error-text">Failed to load results.</p>`;
    }
  });

  clearSearchBtn.addEventListener('click', () => {
    searchInput.value = '';
    searchResultsContent.hidden = true;
    mainContent.hidden = false;
    searchResultsGrid.innerHTML = ''; 
  });

  function renderContextualResults(data, context) {
    searchResultsGrid.innerHTML = ''; 
    let resultsFound = false;

    const renderCategory = (title, items, type) => {
      if (!items || items.length === 0) return;
      resultsFound = true;
      
      const section = document.createElement('section');
      section.className = 'search-category-section';
      section.innerHTML = `<h3>${title}</h3><div class="cards-grid"></div>`;
      
      const grid = section.querySelector('.cards-grid');
      items.forEach(item => {
        // Ensure createContentCard is defined in your JS architecture
        grid.append(createContentCard(type, item)); 
      });
      
      searchResultsGrid.append(section);
    };

    // Use the Django context variable for filtering
    if (context === 'home') {
      renderCategory('Movies', data.movies, 'movie');
      renderCategory('Series', data.series, 'serie');
      renderCategory('Comedies', data.comedies, 'comedy');
      renderCategory('Music', data.music, 'music');
      renderCategory('Visuals', data.visuals, 'visual');
    } else if (context === 'films') {
      renderCategory('Movies', data.movies, 'movie');
      renderCategory('Series', data.series, 'serie');
    } else if (context === 'comedies') {
      renderCategory('Comedies', data.comedies, 'comedy');
    } else if (context === 'music') {
      renderCategory('Music', data.music, 'music');
    }

    if (!resultsFound) {
      searchResultsGrid.innerHTML = `<p class="empty-text">No results found for "${searchTermDisplay.textContent}" in this category.</p>`;
    }
  }
});