function initMap() {
    // Define the coordinates of the parking lot
    var parkingLot = {lat: 37.7749, lng: -122.4194};
  
    // Create a map object centered on the parking lot
    var map = new google.maps.Map(document.getElementById('map'), {
      zoom: 15,
      center: parkingLot
    });
  
    // Create a marker on the parking lot
    var marker = new google.maps.Marker({
      position: parkingLot,
      map: map,
      title: 'Reserved Parking Spot'
    });
  
    // Create a geofence around the parking spot
    var geofence = new google.maps.Circle({
      strokeColor: '#FF0000',
      strokeOpacity: 0.8,
      strokeWeight: 2,
      fillColor: '#FF0000',
      fillOpacity: 0.35,
      map: map,
      center: parkingLot,
      radius: 100 // meters
    });
  
    // Set up a geofencing event listener
    var geofenceListener = google.maps.event.addListener(geofence, 'click', function() {
      alert('You are approaching your reserved parking spot!');
    });
  
    // Create a DirectionsService object
    var directionsService = new google.maps.DirectionsService();
  
    // Define the start and end locations for the route
    var startLocation = null; // Will be set when the user clicks the "Navigate" button
    var endLocation = parkingLot;
  
    // Define the options for the DirectionsRequest
    var directionsRequest = {
      origin: startLocation,
      destination: endLocation,
      travelMode: 'DRIVING'
    };
  
    // Create a DirectionsRenderer object to display the route on the map
    var directionsRenderer = new google.maps.DirectionsRenderer();
    directionsRenderer.setMap(map);
  
    // Define the navigate() function
    function navigate() {
      // Get the user's location using the Geolocation API
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
          startLocation = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
  
          // Update the DirectionsRequest with the user's location
          directionsRequest.origin = startLocation;
  
          // Call the DirectionsService to calculate the route
          directionsService.route(directionsRequest, function(result, status) {
            if (status == 'OK') {
              // Display the route on the map
              directionsRenderer.setDirections(result);
            } else {
              alert('Directions request failed due to ' + status);
            }
          });
        });
      } else {
        alert('Geolocation is not supported by this browser');
      }
    }
  }
  
  window.onload = function() {
    initMap();
  }