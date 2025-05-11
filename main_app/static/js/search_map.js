document.addEventListener('DOMContentLoaded', function() {
    if (!mapboxgl.supported()) {
        document.getElementById('map').innerHTML = `
            <div class="alert alert-warning m-3">
                Your browser does not support WebGL maps.
            </div>
        `;
        return;
    }

    // Initialize map
    const map = new mapboxgl.Map({
        container: 'map',
        style: 'mapbox://styles/mapbox/streets-v11',
        center: [-73.94, 40.7128], // NYC coordinates
        zoom: 10,
        maxBounds: [
            [-75.073700,40.271144], // Southwest corner
            [-72.460327,41.233413]  // Northeast corner
    ]
    });

    // Add controls
    map.addControl(new mapboxgl.NavigationControl());

    // Store restaurant data and markers globally
    let restaurantData = {
        allRestaurants: [],
        inspectionHistory: {},
        currentPage: 1,
        perPage: 10,
        searchLocation: null,
        totalPages: 1
    };
    let restaurantMarkers = [];
    let currentPopup = null;
    let searchMarker = null;

    // Cleanup handler for modals
    document.addEventListener('hidden.bs.modal', function() {
        const backdrops = document.querySelectorAll('.modal-backdrop');
        backdrops.forEach(backdrop => backdrop.remove());
        
        document.body.style.overflow = 'auto';
        document.body.style.paddingRight = '0';
        
        if (map) {
            map.resize();
        }
    });

    // Handle form submission
    document.getElementById('searchForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        const address = document.getElementById('searchAddress').value.trim();
        await handleSearch(address);
    });

    async function handleSearch(address) {
        
        const resultsDiv = document.getElementById('results');
        const errorDiv = document.getElementById('searchError');
        
        resultsDiv.innerHTML = '<div class="text-center my-4"><div class="spinner-border"></div></div>';
        errorDiv.innerHTML = '';
        
        try {
            const response = await fetch('/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ address })
            });
            
            if (!response.ok) {
                const error = await response.json().catch(() => ({ error: 'Search failed' }));
                throw new Error(error.error || 'Search failed');
            }
            
            const data = await response.json();
            
            if (!data.restaurants || !data.inspection_history) {
                throw new Error('Invalid data received from server');
            }
            
            restaurantData = {
                allRestaurants: data.restaurants,
                inspectionHistory: data.inspection_history,
                currentPage: 1,
                perPage: 10,
                searchLocation: data.search_location,
                totalPages: Math.ceil(data.restaurants.length / 10)
            };
            
            displayResultsPage(1);
            updateMap();
            
        } catch (error) {
            resultsDiv.innerHTML = '<p class="text-muted">Enter an NYC address to find nearby restaurants</p>';
            errorDiv.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
            console.error('Search error:', error);
        }
    }

    function getCurrentPageRestaurants() {
        const start = (restaurantData.currentPage - 1) * restaurantData.perPage;
        const end = start + restaurantData.perPage;
        return restaurantData.allRestaurants.slice(start, end);
    }

    function displayResultsPage(page) {
        restaurantData.currentPage = page;
        const currentRestaurants = getCurrentPageRestaurants();
        
        const resultsDiv = document.getElementById('results');
        
        if (!currentRestaurants.length) {
            resultsDiv.innerHTML = `
                <div class="alert alert-info">
                    No restaurants found nearby. Try a different address.
                </div>
            `;
            return;
        }
        
        let html = '<h4 class="mb-3">Nearby Restaurants</h4>';
        
        currentRestaurants.forEach((restaurant, index) => {
            const address = `${restaurant.BUILDING || ''} ${restaurant.STREET || ''}, ${restaurant.BORO || ''}`;
            const gradeClass = restaurant.GRADE ? `grade-${restaurant.GRADE}` : '';
            
            html += `
                <div class="card mb-2 restaurant-card" 
                     data-index="${index}">
                    <div class="card-body">
                        <h5 class="card-title">${restaurant.DBA || 'Unknown'}</h5>
                        <p class="card-text">
                            <small class="text-muted">${address}</small><br>
                            <span class="text-muted small">${restaurant.CUISINE_DESCRIPTION || 'Cuisine not specified'}</span><br>
                            ${restaurant.distance ? `<span>${restaurant.distance.toFixed(2)} miles</span>` : ''}
                            ${restaurant.GRADE ? `<span class="badge ${gradeClass} ms-2">${restaurant.GRADE}</span>` : ''}
                        </p>
                    </div>
                </div>
            `;
        });

        // Add pagination controls
        html += `
        <nav aria-label="Restaurant pagination">
            <ul class="pagination justify-content-center mt-3">
                <li class="page-item ${restaurantData.currentPage === 1 ? 'disabled' : ''}">
                    <a class="page-link" href="#" data-page="${restaurantData.currentPage - 1}">Previous</a>
                </li>
                ${generatePageNumbers(restaurantData.currentPage, restaurantData.totalPages)}
                <li class="page-item ${restaurantData.currentPage === restaurantData.totalPages ? 'disabled' : ''}">
                    <a class="page-link" href="#" data-page="${restaurantData.currentPage + 1}">Next</a>
                </li>
            </ul>
            <div class="text-center text-muted small">
                Page ${restaurantData.currentPage} of ${restaurantData.totalPages} (${restaurantData.allRestaurants.length} total results)
            </div>
        </nav>
        `;
        
        resultsDiv.innerHTML = html;
        
        // Add click handlers to restaurant cards
        document.querySelectorAll('.restaurant-card').forEach(card => {
            card.addEventListener('click', function() {
                const index = parseInt(this.getAttribute('data-index'));
                showMarkerPopup(index);
            });
        });

        // Add click handlers to pagination buttons
        document.querySelectorAll('.page-link').forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const page = parseInt(this.getAttribute('data-page'));
                if (page >= 1 && page <= restaurantData.totalPages) {
                    displayResultsPage(page);
                    updateMap();
                }
            });
        });
    }

    function generatePageNumbers(currentPage, totalPages) {
        let html = '';
        const maxVisiblePages = 5;
        let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
        let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
        
        // Adjust if we're at the end
        if (endPage - startPage + 1 < maxVisiblePages) {
            startPage = Math.max(1, endPage - maxVisiblePages + 1);
        }
        
        if (startPage > 1) {
            html += `<li class="page-item"><a class="page-link" href="#" data-page="1">1</a></li>`;
            if (startPage > 2) {
                html += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
            }
        }
        
        for (let i = startPage; i <= endPage; i++) {
            html += `
                <li class="page-item ${i === currentPage ? 'active' : ''}">
                    <a class="page-link" href="#" data-page="${i}">${i}</a>
                </li>
            `;
        }
        
        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                html += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
            }
            html += `<li class="page-item"><a class="page-link" href="#" data-page="${totalPages}">${totalPages}</a></li>`;
        }
        
        return html;
    }

    function showMarkerPopup(index) {
        if (currentPopup) {
            currentPopup.remove();
            currentPopup = null;
        }
        
        if (restaurantMarkers[index]) {
            map.flyTo({
                center: restaurantMarkers[index].getLngLat(),
                zoom: 17,
                speed: 0.8,
                curve: 1
            });
            
            map.once('moveend', () => {
                currentPopup = restaurantMarkers[index].getPopup();
                restaurantMarkers[index].togglePopup();
            });
        }
    }

    function updateMap() {
        // Clear previous markers
        restaurantMarkers.forEach(marker => marker && marker.remove());
        restaurantMarkers = [];
        currentPopup = null;
        
        // Clear previous search marker (if exists)
        if (searchMarker) {
            searchMarker.remove();
            searchMarker = null;
        }
        
        const currentRestaurants = getCurrentPageRestaurants();
        
        // Create bounds
        const bounds = new mapboxgl.LngLatBounds();
        
        // Add search location marker (red) if available
        if (restaurantData.searchLocation) {
            try {
                searchMarker = new mapboxgl.Marker({ color: '#FF0000' })
                    .setLngLat([
                        restaurantData.searchLocation.lon, 
                        restaurantData.searchLocation.lat
                    ])
                    .setPopup(new mapboxgl.Popup().setHTML(`
                        <h6>Search Location</h6>
                        <p>${restaurantData.searchLocation.label}</p>
                    `))
                    .addTo(map);
                
                bounds.extend([
                    restaurantData.searchLocation.lon, 
                    restaurantData.searchLocation.lat
                ]);
            } catch (e) {
                console.error('Error adding search location marker:', e);
            }
        }
        
        // Add restaurant markers (blue with detailed popups)
        currentRestaurants.forEach((r, index) => {
            if (!r.Longitude || !r.Latitude) return;
            
            try {
                const marker = new mapboxgl.Marker({ color: '#0d6efd' })
                    .setLngLat([r.Longitude, r.Latitude]);
                
                const address = `${r.BUILDING || ''} ${r.STREET || ''}, ${r.BORO || ''}, NY ${r.ZIPCODE || ''}`;
                const gradeClass = r.GRADE ? `grade-${r.GRADE}` : '';
                
                const popupContent = `
                    <div class="map-popup">
                        <h6>${r.DBA || 'Restaurant'}</h6>
                        <p class="mb-1">${address}</p>
                        <p class="mb-1">Cuisine: ${r.CUISINE_DESCRIPTION || 'Not specified'}</p>
                        ${r.PHONE ? `<p class="mb-1">Phone: ${r.PHONE}</p>` : ''}
                        <p class="mb-1">Distance: ${r.distance ? r.distance.toFixed(2) : 'N/A'} miles</p>
                        <p class="mb-1">Grade: <span class="${gradeClass}">${r.GRADE || 'N/A'}</span></p>
                        <button class="btn btn-sm btn-outline-primary w-100 mt-2 view-inspections" 
                                data-camis="${r.CAMIS}">
                            View Inspection History
                        </button>
                    </div>
                `;
                
                const popup = new mapboxgl.Popup({ offset: 25 })
                    .setHTML(popupContent);
                
                marker.setPopup(popup);
                marker.addTo(map);
                
                restaurantMarkers[index] = marker;
                bounds.extend([r.Longitude, r.Latitude]);
                
            } catch (e) {
                console.error('Error creating restaurant marker:', e);
            }
        });
        
        // Fit map to bounds if we have markers
        try {
            if (!bounds.isEmpty()) {
                map.fitBounds(bounds, { 
                    padding: 50, 
                    maxZoom: 15,
                    duration: 500
                });
            }
        } catch (e) {
            console.error('Error fitting map bounds:', e);
        }
        
        // Handle inspection history button clicks in popups
        document.addEventListener('click', function(e) {
            if (e.target.classList.contains('view-inspections')) {
                e.preventDefault();
                e.stopPropagation();

                const camis = e.target.getAttribute('data-camis');
                if (!camis) return;

                // Remove any existing modal first
                const existingModal = bootstrap.Modal.getInstance(document.getElementById('inspectionModal'));
                if (existingModal) {
                    existingModal.hide();
                    document.getElementById('inspectionModalContainer')?.remove();
                }

                const inspections = restaurantData.inspectionHistory[camis];
                if (!inspections) return;

                const modalContainer = document.createElement('div');
                modalContainer.id = 'inspectionModalContainer';
                modalContainer.innerHTML = `
                    <div class="modal fade" id="inspectionModal" tabindex="-1" aria-hidden="true">
                        <div class="modal-dialog modal-lg modal-dialog-scrollable">
                            <div class="modal-content">
                                <div class="modal-header">
                                    <h5 class="modal-title">Inspection History</h5>
                                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                </div>
                                <div class="modal-body">
                                    <table class="table table-striped">
                                        <thead>
                                            <tr>
                                                <th>Date</th>
                                                <th>Grade</th>
                                                <th>Score</th>
                                                <th>Violations</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            ${inspections.map(inspection => `
                                                <tr>
                                                    <td>${inspection.DATE || 'N/A'}</td>
                                                    <td><span class="${inspection.GRADE ? `grade-${inspection.GRADE}` : ''}">
                                                        ${inspection.GRADE || 'N/A'}
                                                    </span></td>
                                                    <td>${inspection.SCORE || 'N/A'}</td>
                                                    <td>${inspection.VIOLATIONS || 'No violations'}</td>
                                                </tr>
                                            `).join('')}
                                        </tbody>
                                    </table>
                                </div>
                                <div class="modal-footer">
                                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;

                document.body.appendChild(modalContainer);
                
                const modal = new bootstrap.Modal(document.getElementById('inspectionModal'));
                
                modal._element.addEventListener('hidden.bs.modal', function() {
                    modal.dispose();
                    modalContainer.remove();
                    
                    const backdrops = document.querySelectorAll('.modal-backdrop');
                    backdrops.forEach(backdrop => backdrop.remove());
                    
                    document.body.style.overflow = 'auto';
                    document.body.style.paddingRight = '0';
                });

                modal.show();
            }
        });
    }
});