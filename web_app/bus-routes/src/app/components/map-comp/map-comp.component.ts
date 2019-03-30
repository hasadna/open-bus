import { Component, OnInit } from '@angular/core';
import { LeafletModule } from '@asymmetrik/ngx-leaflet';
import { icon, latLng, LatLng, Layer, marker, tileLayer } from 'leaflet';
import { environment } from '../../../environments/environment';
import { MapMngrService } from 'src/app/services/map-mngr/map-mngr.service';
import { BusStop } from 'src/app/data/bus-stop';

@Component({
  selector: 'app-map-comp',
  templateUrl: './map-comp.component.html',
  styleUrls: ['./map-comp.component.less']
})
export class MapCompComponent implements OnInit {
  private API_URL = environment.streetViewUrl;
  markers: Layer[] = [];

  optionsSpec: any = {
		layers: [{ url: `${this.API_URL}`, attribution: 'Open Street Map' }],
		zoom: 12,
		center: [ 32.073715147149684, 34.809556706163754 ]
	};

	// Leaflet bindings
	zoom = this.optionsSpec.zoom;
	center = latLng(this.optionsSpec.center);
	options = {
		layers: [ tileLayer(this.optionsSpec.layers[0].url, { attribution: this.optionsSpec.layers[0].attribution }) ],
		zoom: this.optionsSpec.zoom,
		center: latLng(this.optionsSpec.center)
	};
  constructor(private mapMngrService: MapMngrService){}

  	// Output binding for center
	onCenterChange(center: LatLng) {
		;
	}

	onZoomChange(zoom: number) {
	  ;
  }

  addStop(stop: BusStop){
    const newMarker = marker(
			[ stop.geometry.coordinates[0], stop.geometry.coordinates[1] ],
			{
				icon: icon({
					iconSize: [ 25, 41 ],
					iconAnchor: [ 13, 41 ],
					iconUrl: 'marker-icon.png',
					//shadowUrl: 'marker-shadow.png'
				})
			}
		);

		this.markers.push(newMarker);
  }

  ngOnInit() {
    this.mapMngrService.loadTrip(1);
/*
    const stopsJson = [
      {
        "type": "Feature",
        "geometry": {
          "type": "Point",
          "coordinates": [
            32.178298,
            34.926906
          ]
        },
        "properties": {
          "stop_code": "37064",
          "stop_id": "24430"
        }
      }
    ];*/


    let busStop = new BusStop();
    busStop.geometry = {
      "type": "Point",
      "coordinates": [
        32.178298,
        34.926906
      ]
    };
    busStop.properties = {
      "stop_code": 37064,
      "stop_id": 24430
    };
    busStop.type = "Feature";

    this.addStop(busStop);
  }
}
