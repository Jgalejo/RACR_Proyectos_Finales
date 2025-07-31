// Main script for form handling and SPARQL queries
const form = document.getElementById('game-form');
const resultsGrid = document.getElementById('results-grid');
const loader = document.getElementById('loader');
const noResults = document.getElementById('no-results');
const dbpediaEndpoint = 'https://dbpedia.org/sparql';

// Elements for debugging display
const queryDisplaySection = document.getElementById('query-display-section');
const sparqlQueryOutput = document.getElementById('sparql-query-output');

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    resultsGrid.innerHTML = '';
    noResults.classList.add('hidden');
    loader.classList.remove('hidden');

    const formData = new FormData(form);
    const preferences = Object.fromEntries(formData.entries());

    const sparqlQuery = buildSparqlQuery(preferences);
    
    // --- DEBUGGING ---
    // Log the query to the browser's console
    console.log('Generated SPARQL Query:', sparqlQuery);
    // Display the query on the page
    sparqlQueryOutput.textContent = sparqlQuery;
    queryDisplaySection.classList.remove('hidden');
    // --- END DEBUGGING ---

    try {
        const response = await fetch(dbpediaEndpoint + '?query=' + encodeURIComponent(sparqlQuery) + '&format=json');
        if (!response.ok) {
            throw new Error(`Error en la consulta SPARQL: ${response.statusText}`);
        }
        const data = await response.json();
        displayResults(data.results.bindings);
    } catch (error) {
        console.error('Error fetching data:', error);
        noResults.textContent = 'Ocurrió un error al conectar con DBpedia. Inténtalo de nuevo más tarde.';
        noResults.classList.remove('hidden');
    } finally {
        loader.classList.add('hidden');
    }
});

function buildSparqlQuery(prefs) {
    let filters = '';
    
    if (prefs.genre) {
        filters += `?game dbo:genre ?genreUri . FILTER(CONTAINS(STR(?genreUri), "${prefs.genre}"))\n`;
    }
    if (prefs.platform) {
        filters += `?game dbp:platforms ?platform . FILTER(CONTAINS(STR(?platform), "${prefs.platform}"))\n`;
    }
    if (prefs.releaseYearFrom) {
        filters += `FILTER(YEAR(?releaseDate) >= ${prefs.releaseYearFrom})\n`;
    }
    if (prefs.releaseYearTo) {
        filters += `FILTER(YEAR(?releaseDate) <= ${prefs.releaseYearTo})\n`;
    }
    // Use REGEX for case-insensitive search on manual inputs
    if (prefs.developer) {
        filters += `?game dbo:developer ?developer . FILTER(REGEX(STR(?developer), "${prefs.developer}", "i"))\n`;
    }
    if (prefs.publisher) {
        filters += `?game dbo:publisher ?publisher . FILTER(REGEX(STR(?publisher), "${prefs.publisher}", "i"))\n`;
    }
    if (prefs.gameMode) {
         filters += `?game dbo:gameMode ?mode . FILTER(CONTAINS(STR(?mode), "${prefs.gameMode}"))\n`;
    }

    return `
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>

        SELECT DISTINCT ?game ?title ?releaseDate ?abstract  (GROUP_CONCAT(DISTINCT ?genreName; SEPARATOR=", ") AS ?genres)
        WHERE {
            ?game a dbo:VideoGame .
            ?game rdfs:label ?title .
            ?game dbo:releaseDate ?releaseDate .
            ?game dbo:abstract ?abstract .
            
            OPTIONAL { ?game dbo:thumbnail ?thumbnail . }
            OPTIONAL { 
                ?game dbo:genre ?genreUri .
                ?genreUri rdfs:label ?genreName .
                FILTER(LANG(?genreName) = "en")
            }

            ${filters}

            FILTER(LANG(?title) = "en")
            FILTER(LANG(?abstract) = "en")
        }
        GROUP BY ?game ?title ?releaseDate ?abstract ?thumbnail
        ORDER BY DESC(?releaseDate)
        LIMIT 10
    `;
}

function displayResults(bindings) {
    if (bindings.length === 0) {
        noResults.classList.remove('hidden');
        return;
    }

    bindings.forEach(item => {
        const title = item.title?.value || 'Título no disponible';
        const abstract = item.abstract?.value || 'Sin descripción.';
        const releaseYear = item.releaseDate ? new Date(item.releaseDate.value).getFullYear() : 'N/A';
        const imageUrl = item.thumbnail?.value || `https://placehold.co/400x300/16192a/00ffff?text=${encodeURIComponent(title)}`;
        const gameUrl = item.game.value;
        const genres = item.genres?.value || 'Género no especificado';

        const card = document.createElement('div');
        card.className = 'card rounded-lg overflow-hidden flex flex-col';
        card.innerHTML = `
            <a href="${gameUrl}" target="_blank" rel="noopener noreferrer">
                <img src="${imageUrl}" alt="Imagen de ${title}" class="w-full h-48 object-cover" onerror="this.onerror=null;this.src='https://placehold.co/400x300/16192a/e0e0e0?text=Sin+Imagen';">
            </a>
            <div class="p-4 flex flex-col flex-grow">
                <h3 class="text-xl font-bold text-cyan-300 mb-2 truncate" title="${title}">${title}</h3>
                <p class="text-sm text-purple-300 mb-2"><strong>Año:</strong> ${releaseYear}</p>
                <p class="text-sm text-purple-300 mb-3"><strong>Géneros:</strong> ${genres}</p>
                <p class="text-gray-400 text-sm flex-grow">${abstract.substring(0, 100)}...</p>
                <a href="${gameUrl}" target="_blank" rel="noopener noreferrer" class="mt-4 text-center text-cyan-400 font-semibold hover:text-white transition-colors duration-300">
                    Ver en DBpedia &rarr;
                </a>
            </div>
        `;
        resultsGrid.appendChild(card);
    });
}