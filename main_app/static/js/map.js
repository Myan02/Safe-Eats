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
        center: [-74.0060, 40.7128],
        zoom: 12
    });

    // Add controls
    map.addControl(new mapboxgl.NavigationControl());

    // Handle form submission
    document.getElementById('searchForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        const address = document.getElementById('searchAddress').value.trim();
        const resultsDiv = document.getElementById('results');
        const errorDiv = document.getElementById('searchError');
        
        // Clear previous
        resultsDiv.innerHTML = '<div class="text-center my-4"><div class="spinner-border"></div></div>';
        errorDiv.innerHTML = '';
        
        try {
            const response = await fetch('/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ address })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Search failed');
            }
            
            displayResults(data.restaurants);
            updateMap(data.search_location, data.restaurants);
            
        } catch (error) {
            resultsDiv.innerHTML = '<p class="text-muted">Enter an NYC address to find nearby restaurants</p>';
            errorDiv.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
        }
    });

    function displayResults(restaurants) {
        const resultsDiv = document.getElementById('results');
        
        if (!restaurants || restaurants.length === 0) {
            resultsDiv.innerHTML = `
                <div class="alert alert-info">
                    No restaurants found nearby. Try a different address.
                </div>
            `;
            return;
        }
        
        let html = '<h4 class="mb-3">Nearby Restaurants</h4>';
        
        restaurants.forEach(restaurant => {
            const address = `${restaurant.BUILDING || ''} ${restaurant.STREET || ''}, ${restaurant.BORO || ''}`;
            const gradeClass = restaurant.GRADE ? `grade-${restaurant.GRADE}` : '';
            
            html += `
                <div class="card mb-2">
                    <div class="card-body">
                        <h5 class="card-title">${restaurant.DBA || 'Unknown'}</h5>
                        <p class="card-text">
                            <small class="text-muted">${address}</small><br>
                            ${restaurant.distance ? `<span>${restaurant.distance.toFixed(2)} miles</span>` : ''}
                            ${restaurant.GRADE ? `<span class="badge ${gradeClass} ms-2">${restaurant.GRADE}</span>` : ''}
                        </p>
                    </div>
                </div>
            `;
        });
        
        resultsDiv.innerHTML = html;
    }

    function updateMap(searchLocation, restaurants) {
        // Clear existing markers
        document.querySelectorAll('.mapboxgl-marker').forEach(m => m.remove());
        
        // Create bounds
        const bounds = new mapboxgl.LngLatBounds();
        
        // Add search location marker
        new mapboxgl.Marker({ color: '#FF0000' })
            .setLngLat([searchLocation.lon, searchLocation.lat])
            .setPopup(new mapboxgl.Popup().setHTML(`
                <h6>Search Location</h6>
                <p>${searchLocation.label}</p>
            `))
            .addTo(map);
            
        bounds.extend([searchLocation.lon, searchLocation.lat]);
        
        // Add restaurant markers
        restaurants.forEach(r => {
            if (r.Longitude && r.Latitude) {
                const marker = new mapboxgl.Marker()
                    .setLngLat([r.Longitude, r.Latitude])
                    .setPopup(new mapboxgl.Popup().setHTML(`
                        <h6>${r.DBA || 'Restaurant'}</h6>
                        <p>${r.BUILDING || ''} ${r.STREET || ''}</p>
                        <p>Grade: <span class="${r.GRADE ? `grade-${r.GRADE}` : ''}">${r.GRADE || 'N/A'}</span></p>
                        ${r.distance ? `<p>Distance: ${r.distance.toFixed(2)} miles</p>` : ''}
                    `))
                    .addTo(map);
                    
                bounds.extend([r.Longitude, r.Latitude]);
            }
        });
        
        // Fit map to bounds
        if (!bounds.isEmpty()) {
            map.fitBounds(bounds, { padding: 50, maxZoom: 15 });
        }
    }
});