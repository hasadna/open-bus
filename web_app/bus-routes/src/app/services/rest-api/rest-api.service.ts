import { Injectable } from '@angular/core';
import { environment } from '../../../environments/environment';
//import {HttpParams} from  "@angular/common/http";
import { HttpClient } from  "@angular/common/http";
import { Trip } from 'src/app/data/trip';
import { Observable } from 'rxjs/internal/Observable';

const API_URL = environment.busRestApiUrl;

@Injectable({
  providedIn: 'root'
})
export class RestApiService {
      constructor(private httpClient: HttpClient) {}

    // API: GET /todos
    /*
  public getTripById(tripNumber: number): Observable<Trip>{
    const trip: Observable<Trip> = this.httpClient.get(`${API_URL}/trips/${tripNumber}`);
    return trip;
  }*/

  public getTripById(tripNumber: number){
    const trip = this.httpClient.get(`${API_URL}/trips/${tripNumber}`);
    return trip;
  }

  //Not implemented at server side!
  public getTrips(url?: string){
    return this.httpClient.get<Trip[]>(`${API_URL}/trips`);
  }
}

