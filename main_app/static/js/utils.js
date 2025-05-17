// return a match statement for the layer styling
export async function updateZipcodes() {
    try {
        // retrieve the average grade for each zipcode and its assigned color
        const response = await fetch("/fetch_means");

        if (!response.ok) {
            throw new Error("Couldn't get average grades per zipcode from utils.js...");
        }
        const zipcodeEntries = await response.json();

        // set up the initial properties of the match expression, we want to match each zipcode (hence postalCode in geoJSON) with a color
        let matchExpression = ["match", ["get", "postalCode"]]; 

        // iterate over each zipcode and set each zipcode to a color
        zipcodeEntries.forEach(entry => {
            
            const zipcode = String(entry.ZIPCODE);  // Ensure zipcode is a string
            const color = entry.COLOR;

            matchExpression.push(zipcode, color);   // add it to the expression! (its just an array)
        });

        matchExpression.push("#cccccc"); // default color for a zipcode that doesn't exist 

        return matchExpression;
    }
    catch (error) {
        console.error(`Error fetching zipcode colors: ${error}`);
    }
}


// retrieve all unique restaurants, this should only be ran ONCE
let restaurantsByZipcode = {};  // we set this global variable and then the map.js requests it when needed
export async function getUniqueRestaurants() {

    try {
        // get an object containing all unique restaurants
        const response = await fetch("/fetch_unique_restaurants");
        
        if (!response.ok) {
            throw new Error("Couldn't get all unique restaurants from utils.js...");
        }
        const restaurants = await response.json();
        
        restaurants.forEach(restaurant => {

            const zipcode = restaurant.ZIPCODE;     // get the current restaurant's zipcode

            if (!restaurantsByZipcode[zipcode]) {   // if the zipcode doesn't exist in the array yet, add it!
                restaurantsByZipcode[zipcode] = [];
            }

            restaurantsByZipcode[zipcode].push(restaurant); // add the restaurant to the zipcode array
        });

        // we don't need to return anything, all data is referenced in the restaurantsByZipcode array and retrieved later
    }
    catch(error) {
        console.error(error);
    }
}

// this function just returns the zipcode array, its kinda dumb but it works
export function getRestaurantsByZipcode() {
    return restaurantsByZipcode;
}

// map each grade to a color value for the markers
export function calculateColorGrade(grade) {

    switch (grade) {
        case "A":
            return "#0063b0";   // blue
        
        case "B":
            return "#48AC42";   // green
        
        case "C":   
            return "#F9992B";   // red
        
        default:
            return "#d9d9d9";   // gray
    }
}