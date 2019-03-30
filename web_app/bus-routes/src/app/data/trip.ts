import { BusStop } from './bus-stop';

export interface Trip{
  tripId: string;
  planned_time: string;
  date: string;
  routeId: number;
  routeShortName: string;
  routeLongName: string;
  agencyName: string;
  routeType: number;
  stops: BusStop;
  startZone: string;
  endZone: string;
  isLoop: number;
  distance: object;
  duration: number;
  speed: number;
  shape: object;
  siri:object;
}
