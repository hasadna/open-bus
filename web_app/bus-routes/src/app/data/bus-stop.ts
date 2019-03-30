class Geometry {
  type: string;
  coordinates: number[];
}

class Properties {
  stop_code: number;
  stop_id: number;
}

export class BusStop {
  /*
  constructor(type:string, geometry: Geometry, properties: Properties) {
    this.type = type;
    this.geometry = geometry;
    this.properties = properties;
 }*/

 constructor(){}
  type: string;
  geometry: Geometry;
  properties: Properties;
}
