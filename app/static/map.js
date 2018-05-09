function myMap() {
    var mapCanvas = document.getElementById("googleMap");
    var myCenter = new google.maps.LatLng(53.79, -1.549);
    var mapOptions = {
        styles: [{
            "featureType": "administrative.country",
            "stylers": [{
                "visibility": "off"
            }]
        }, {
            "featureType": "administrative.country",
            "elementType": "geometry.stroke",
            "stylers": [{
                "visibility": "off"
            }]
        }, {
            "featureType": "landscape",
            "stylers": [{
                "visibility": "off"
            }]
        }, {
            "featureType": "transit",
            "stylers": [{
                "visibility": "off"
            }]
        }, {
            "featureType": "water",
            "stylers": [{
                "visibility": "simplified"
            }]
        }, {
            "featureType": "water",
            "stylers": [{
                "color": "#ffffff"
            }]
        }, {
            "featureType": "road",
            "stylers": [{
                "visibility": "off"
            }]
        }, {
            "featureType": "transit",
            "stylers": [{
                "visibility": "off"
            }]
        }, {
            "featureType": "administrative",
            "stylers": [{
                "visibility": "off"
            }]
        }, {
            "featureType": "poi",
            "stylers": [{
                "visibility": "off"
            }]
        }, {
            "featureType": "transit",
            "stylers": [{
                "visibility": "off"
            }]
        }, {
            "featureType": "landscape",
            "stylers": [{
                "visibility": "on"
            }, {
                "color": "#e3e1e1"
            }]
        }, {
            "featureType": "water",
            "stylers": [{
                "visibility": "simplified"
            }, {
                "color": "#ffffff"
            }]
        }],
        center: myCenter,
        zoom: 6,
        draggable: false,
        zoomControl: false,
        scrollwheel: false,
        disableDoubleClickZoom: true,
        streetViewControl: false,
        disableDefaultUI: true,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    var label1 = 'London';
    var label2 = 'Leeds';
    var label3 = 'Glasgow';
    var image1 = 'static/cities/london.png';
    var image2 = 'static/cities/leeds.png';
    var image3 = 'static/cities/glasgow.png';
    var map = new google.maps.Map(mapCanvas, mapOptions);
    var marker1 = new google.maps.Marker({
        position: new google.maps.LatLng(51.5, -0.120850),
        title: label1,
        icon: image1
    });
    var marker2 = new google.maps.Marker({
        position: new google.maps.LatLng(53.79, -1.549),
        title: label2,
        icon: image2
    });
    var marker3 = new google.maps.Marker({
        position: new google.maps.LatLng(55.85, -4.26),
        title: label3,
        icon: image3
    });


    marker1.setMap(map);
    marker2.setMap(map);
    marker3.setMap(map);



    google.maps.event.addListener(marker1, 'click', function() {
        window.location.href = '/courses/London';
    });
    google.maps.event.addListener(marker2, 'click', function() {
        window.location.href = '/courses/Leeds';
    });
    google.maps.event.addListener(marker3, 'click', function() {
        window.location.href = '/courses/Glasgow';
    });
}
