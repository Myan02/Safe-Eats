// MapBox Access Token
mapboxgl.accessToken = "";  // Replace this with your own!

// Initialize Mapbox map
var map = new mapboxgl.Map({
    container: "map",
    style: "mapbox://styles/mapbox/light-v11",
    center: [-74.0060, 40.7128], // NYC coordinates
    zoom: 10,
    maxBounds: [
        [-75.073700,40.271144], // Southwest corner
        [-72.460327,41.233413]  // Northeast corner
    ]
});

// run as the map gets loaded in 
map.on('load', () => {
    map.addSource('zipcodes', {
        type: 'geojson',
        data: '/zipcode_borders/nyc_zipcode_borders_with_grades.geojson'
    });

    map.addLayer({
        id: 'zipcode-fill',
        type: 'fill',
        source: 'zipcodes',
        paint: {
            'fill-color': 'orange'
        }
    }, 'settlement-minor-label');

    updateZipcodes();

    map.addLayer({
        id: 'zipcode-borders',
        type: 'line',
        source: 'zipcodes',
        paint: {
            'line-color': '#ffffff',
            'line-width': 1
        }
    }, 'settlement-minor-label');


    map.setPaintProperty("settlement-major-label", "text-color", "#000000")
    map.setPaintProperty("settlement-minor-label", "text-color", "#000000")

});


async function updateZipcodes(){
    try {
        const response = await fetch("http://127.0.0.1:5000/inspections/get_average_grades");
        const zipcode_entries = await response.json();

        let matchExpression = ["match", ["get", "modzcta"]]; 

        zipcode_entries.forEach(entry => {
            
            const zipcode = String(entry.zipcode);  // Ensure zipcode is a string
            const color = entry.color;

            matchExpression.push(zipcode, color);
        });

        matchExpression.push("#cccccc"); // default color

        if (map.getLayer("zipcode-fill")) {
            map.setPaintProperty("zipcode-fill", "fill-color", matchExpression);
            map.setPaintProperty("zipcode-fill", "fill-opacity", 0.75);  // Adjust opacity (0 = fully transparent, 1 = fully opaque)
        } else {
            console.error("Layer 'zipcode-fill' not found!");
        }
    }
    catch (error){
        console.error(`Error fetching zipcode colors: ${error}`);
    }
}

// // retrieve inspection data
// getData();
// async function getData(){

//     try{
//         // HTTP request gets a response object
//         const response = await fetch("/restaurants");
        
//         // response returns 200 if it is ok
//         if (!response.ok){
//             throw new Error("Unable to fetch inspection results.");
//         }

//         // create a new marker for each inspection entry
//         const inspectionData = await response.json();
//         inspectionData.forEach(inspection => {
//             // check to make sure coordinates exist
//             if (inspection.latitude !== 'undefined' && inspection.latitude > 0) {
//                 new mapboxgl.Marker({
//                     color: calculateColorGrade(inspection.grade),
//                     scale: 0.5,
//                 }).setLngLat([inspection.longitude, inspection.latitude])   // set location
//                   .setPopup(
//                     new mapboxgl.Popup().setHTML(`<h1>${inspection.dba}</h1>`)
//                   )     // set click content
//                   .addTo(map)
//             }
            
//         });
//     }
//     catch(error){
//         console.error(error);
//     }
// }

// return a color based on grade
function calculateColorGrade(grade){
    switch (grade){
        case "A":
            return "#0063b0";   // blue
        
        case "B":
            return "#48AC42";   // green
        
        case "C":   
            return "#F9992B";   // red
        
        default:
            return "#d9d9d9";   // grat
    }
}
