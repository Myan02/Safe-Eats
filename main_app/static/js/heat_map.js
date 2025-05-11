import { updateZipcodes,
         getUniqueRestaurants, 
         calculateColorGrade,
         getRestaurantsByZipcode 
} from "./utils.js";

// Initialize Mapbox map
var map = new mapboxgl.Map({
    container: "map",
    style: "mapbox://styles/mapbox/light-v11",
    center: [-73.94, 40.7128], // NYC coordinates
    zoom: 10,
    minZoom: 10,
    maxBounds: [
        [-75.073700,40.271144], // Southwest corner
        [-72.460327,41.233413]  // Northeast corner
    ]
});

// global variables
let all_restaurant_markers = [];    // store all markers, each marker represents a restaurant
let all_restaurant_popups = [];     // store all popups for restaurants
let isHoveringMarker = false;       // if true, the map will allow you to hover over a marker 
let currentZipcode = 0;             // keeps track of the current zipcode the user is hovering over
let zoomedIn = false;

// single popup to display overview, shows info about average grade
const zipcode_popup = new mapboxgl.Popup({
    closeButton: false,
    closeOnClick: false
});


// run as the map gets loaded in (like a map constructor)
map.on('load', async () => {
    // load in geojson data called 'zipcodes'
    map.addSource('zipcodes', {
        type: 'geojson',
        data: '/fetch_geoms'
    });

    // add a new layer for the zipcode shading
    map.addLayer({
        id: 'zipcode-fill',     // layer reference
        type: 'fill',           // says to fill in each area 
        source: 'zipcodes',     // data comes from this source loaded previously
        paint: {
            'fill-color': 'orange'  // default color in case the actual colors dont work
        }
    });   // put this layer behind the settlement-minor-label layer so we can see some titles over the map

    const matchExpression = await updateZipcodes();       // get match expression to match colors to grades

    // set color of each zipcode
    map.setPaintProperty("zipcode-fill", "fill-color", matchExpression);
    map.setPaintProperty("zipcode-fill", "fill-opacity", 0.75);  // Adjust opacity (0 = fully transparent, 1 = fully opaque)

    // add a new layer for the zipcode borders
    map.addLayer({
        id: 'zipcode-borders',  // layer reference
        type: 'line',           // says to fill in the borders
        source: 'zipcodes',     // data comes from this source loaded previously
        paint: {
            'line-color': '#ffffff',    // set each border color to white
            'line-width': 1             // set the border thickness to 1
        }
    });       // put this layer behind the settlement-minor-label layer so we can see some titles over the map

    // add the zoom in, zoom out, and compass buttons to the map
    map.addControl(new mapboxgl.NavigationControl());

    // set some styling for the map 
    map.setPaintProperty("settlement-major-label", "text-color", "#000000")     // set the titles to be black
    map.setPaintProperty("settlement-minor-label", "text-color", "#000000")     // set the smaller titles to be black

    console.log(map.getStyle().layers);

    // once ready, sets the restaurantByZipcode array found in helper.js
    await getUniqueRestaurants();
});

map.on('zoom', () => {
    const zoomLevel = map.getZoom();
    
    if (zoomLevel > 13) {
        zoomedIn = true
    }
    else {
        zoomedIn = false
    }
})


// call when the mouse moves over ny, run this function at every mouse movement
map.on('mousemove', 'zipcode-fill', (e) => {

    // change the mouse cursor to a pointer 🤓☝
    map.getCanvas().style.cursor = 'pointer';

    // query whatever data the mouse is on
    const response = map.queryRenderedFeatures(e.point)[0];

    // these are the properties we care about
    const properties = {
        "zipcode": response.properties.postalCode,
        "average_grade": response.properties.MEAN,
        "color": response.properties.COLOR
    }

    // how zoomed in are ya?
    const zoomLevel = map.getZoom();

    // if zoomed in... do a lot more lol
    if (zoomedIn) {

        // remove the big popup and reset the cursor
        zipcode_popup.remove();
        map.getCanvas().style.cursor = '';

        // only load new information if a new zipcode is hovered over, else just keep the data how it is
        if (properties.zipcode == currentZipcode) {
            isHoveringMarker = true;
            return;
        }
        else {

            // clear and reset all old markers
            all_restaurant_markers.forEach(marker => marker.remove());
            all_restaurant_markers = [];

            // clear and reset all old popups
            all_restaurant_popups.forEach(popup => popup.remove());
            all_restaurant_popups = [];

            // get an array of all restaruants in the zipcode pointed to (or nothing if it doesn't exist)
            const nearbyRestaurants = getRestaurantsByZipcode()[properties.zipcode] || [];

            // set the current zipcode to ensure this block of code only gets ran ONCE per zipcode 
            currentZipcode = nearbyRestaurants[0].ZIPCODE;

            // do something for each restaurant in this zipcode
            nearbyRestaurants.forEach(restaurant => {

                const gradeClass = restaurant.GRADE ? `grade-${restaurant.GRADE}` : '';

                // create a popup to show the restaurants name and grade
                const popup = new mapboxgl.Popup({
                    'closeOnMove': false,
                    'closeButton': false,
                    'closeOnClick': true
                })
                .setHTML(`
                    <div class="map-popup">
                        <h6>${restaurant.DBA}</h6>
                        <p class="mb-1">Grade: <span class="${gradeClass}">${restaurant.GRADE || 'N/A'}</span></p>
                    </div>
                `);

                // create a marker with the same color as its grade
                const marker = new mapboxgl.Marker({
                    'color': calculateColorGrade(restaurant.GRADE),
                    'scale': 0.65
                })
                .setLngLat([restaurant.Longitude, restaurant.Latitude])
                .setPopup(popup)
                .addTo(map)

                // put all markers and popups in an array, we need to keep track of them so we can delete them later
                all_restaurant_markers.push(marker);
                all_restaurant_popups.push(popup);
            });

            // set the background of the zipcode to be actually visible
            map.setPaintProperty("zipcode-borders", "line-width", ["match", ["get", "postalCode"], properties.zipcode, 3, 1]);
            map.setPaintProperty("zipcode-borders", "line-color", ["match", ["get", "postalCode"], properties.zipcode, "#999999", "#ffffff"]);
            map.setPaintProperty("zipcode-fill", "fill-opacity", ["match", ["get", "postalCode"], properties.zipcode, 0, 0.75]);
        
            // we don't need to do anything else
            return;
        }

}

    // clear and reset all old markers
    all_restaurant_markers.forEach(marker => marker.remove());
    all_restaurant_markers = [];

    // clear and reset all old popups
    all_restaurant_popups.forEach(popup => popup.remove());
    all_restaurant_popups = [];

    // reset current zipcode and don't turn off marker hovering
    currentZipcode = 0;
    isHoveringMarker = false;

    console.log(properties.average_grade)

    // show a popup for the zipcode and the average grade of the zipcode
    zipcode_popup
        .setLngLat(e.lngLat)
        .setHTML(`
            <div class="map-popup" id="heatmap-main-popup">
                <h6 id="heatmap-zipcode">Zipcode: ${properties.zipcode}</h6>
                <p class="mb-1" id="heatmap-average">Average Grade: <span">${parseFloat(properties.average_grade).toFixed(2) || 'N/A'}</span></p>
            </div>
                `)
        .addTo(map);

    
    // change the border so its highlighted, makes it a lil easier to see
    map.setPaintProperty("zipcode-borders", "line-width", ["match", ["get", "postalCode"], properties.zipcode, 5, 1]);
    map.setPaintProperty("zipcode-borders", "line-color", ["match", ["get", "postalCode"], properties.zipcode, "#999999", "#ffffff"]);
    map.setPaintProperty("zipcode-fill", "fill-opacity", 0.75);
});


// call this when the mouse leaves ny
map.on('mouseleave', 'zipcode-fill', (e) => {


    if (isHoveringMarker == true) {
        return;
    }
    else {
        // reset the cursor and remove the big popup
        map.getCanvas().style.cursor = '';
        zipcode_popup.remove();
    
        // reset the layer style properties (i should put this into a reset style function...)
        map.setPaintProperty("zipcode-borders", "line-width", 1);
        map.setPaintProperty("zipcode-borders", "line-color", "#ffffff");
        map.setPaintProperty("zipcode-fill", "fill-opacity", 0.75);
    
        // reset all markers, popups, and the current zipcode
        all_restaurant_markers.forEach(marker => marker.remove());
        all_restaurant_markers = [];
        all_restaurant_popups.forEach(popup => popup.remove());
        all_restaurant_popups = [];
        currentZipcode = 0;
    }
    
});