
OpenLayers.ImgPath = "/esco/media/img/openlayers/";

pilsen_lon = 13.38660;
pilsen_lat = 49.74520;

pilsen_zoom = 15;

var map;

/*
  49.747523,13.393169 Angelo
  49.746576,13.386065 Spilka
  49.747740,13.380572 Marriott
*/

$(document).ready(function() {
    function osmLonLat(lon, lat) {
        return
    }

    function createMap() {
        map = new OpenLayers.Map("map", {
            controls: [
                new OpenLayers.Control.DragPan(),
                new OpenLayers.Control.ScaleLine(),
                new OpenLayers.Control.PanZoomBar(),
                new OpenLayers.Control.LayerSwitcher(),
            ],
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
    }

    function centerMap() {
        map.setCenter(new OpenLayers.LonLat(pilsen_lon, pilsen_lat), pilsen_zoom);
    }

    createMap();
    centerMap();
});

