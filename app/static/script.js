// MapBox Access Token
mapboxgl.accessToken = "pk.eyJ1IjoibWJhYnVyeWFuIiwiYSI6ImNtOHY1ZzB1dTBzd2QyaW9qYXpranhuczAifQ.GvZ-Yc6um283djoYZbe3BA";  // Replace this!

// Initialize Mapbox map
var map = new mapboxgl.Map({
    container: "map",
    style: "mapbox://styles/mapbox/streets-v11",
    center: [-74.0060, 40.7128], // NYC coordinates
    zoom: 10
});

// retrieve inspection data
getData();
async function getData(){

    try{
        // HTTP request gets a response object
        const response = await fetch("/restaurants");
        
        // response returns 200 if it is ok
        if (!response.ok){
            throw new Error("Unable to fetch inspection results.");
        }

        // create a new marker for each inspection entry
        const inspectionData = await response.json();
        inspectionData.forEach(inspection => {
            new mapboxgl.Marker({
                color: calculateColorGrade(inspection.grade),
                scale: 0.5,
            }).setLngLat([inspection.longitude, inspection.latitude])   // set location
              .setPopup(
                new mapboxgl.Popup().setHTML(`<h1>${inspection.dba}</h1>`)
              )     // set click content
              .addTo(map)
        });
    }
    catch(error){
        console.error(error);
    }
}

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
