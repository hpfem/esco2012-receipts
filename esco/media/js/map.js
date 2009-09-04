
OpenLayers.ImgPath = "/events/esco-2010/media/img/openlayers/";

pilsen_lon = 13.38500;
pilsen_lat = 49.74520;

pilsen_zoom = 15;

var map;
var icon;

coords = {
    'Angelo': new OpenLayers.LonLat(13.393169, 49.747523),
    'Spilka': new OpenLayers.LonLat(13.386065, 49.746576),
    'Marriott': new OpenLayers.LonLat(13.380572, 49.747740),
};

default_feature_style = {
    strokeDashstyle: "solid",
    pointerEvents: "visiblePainted",
    fillColor: "#ffcc66",
    strokeColor: "#ff9933",
    pointRadius: 5,
    strokeWidth: 3,
};

popups = {};

$(document).ready(function() {
    function createMap() {
        map = new OpenLayers.Map("map", {
            controls: [
                new OpenLayers.Control.DragPan(),
                new OpenLayers.Control.ScaleLine(),
                new OpenLayers.Control.PanZoomBar(),
                new OpenLayers.Control.LayerSwitcher(),
            ],
            minResolution: "auto",
            minExtent: new OpenLayers.Bounds(-1, -1, 1, 1),
            maxResolution: "auto",
            maxExtent: new OpenLayers.Bounds(-180, -90, 180, 90),
        });

        map.controls[0].activate();

        gmap = new OpenLayers.Layer.Google(
            "Google Streets",
            {numZoomLevels: 20}
        );

        ghyb = new OpenLayers.Layer.Google(
            "Google Hybrid",
            {type: G_HYBRID_MAP, numZoomLevels: 20}
        );

        gsat = new OpenLayers.Layer.Google(
            "Google Satellite",
            {type: G_SATELLITE_MAP, numZoomLevels: 20}
        );

        map.addLayers([gmap, ghyb, gsat]);

        size = new OpenLayers.Size(24, 38);
        offset = new OpenLayers.Pixel(-(size.w/2), -size.h);

        points = new OpenLayers.Layer.Markers("POI");
        map.addLayer(points);

        for (key in coords) {
            icon = new OpenLayers.Icon("/events/esco-2010/media/img/marker.png", size, offset);
            marker = new OpenLayers.Marker(coords[key], icon);
            points.addMarker(marker);
        }
    }

    function centerMap() {
        map.setCenter(new OpenLayers.LonLat(pilsen_lon, pilsen_lat), pilsen_zoom);
    }

    createMap();
    centerMap();
});

