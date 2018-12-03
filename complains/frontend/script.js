var map = L.map('mapid').setView([32.073608, 34.790128], 17);

map.scrollWheelZoom.disable();

// TODO: Create new `access_token`
L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw', {
    maxZoom: 18,
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
        '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
        'Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    id: 'mapbox.streets'
}).addTo(map);

var busStationIcon = L.icon({
    iconUrl: 'bus_station_icon.svg',
    iconSize:     [38, 38], // size of the icon
});

var customPopup = "Test";
// specify popup options
var customOptions = {
    'maxWidth': '1000',
    'className' : 'custom'
}


L.marker([32.073539, 34.789106], {icon: busStationIcon}).bindPopup(customPopup,customOptions).addTo(map);
