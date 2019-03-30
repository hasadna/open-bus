import { Injectable } from '@angular/core';
import { RestApiService } from 'src/app/services/rest-api/rest-api.service';

@Injectable({
  providedIn: 'root'
})
export class MapMngrService {
  constructor(private restApiService: RestApiService) {
  }

  public loadTrip(tripNumber: number) {
    //Get tripId number 1 from server, later will be changed to buttons and so on
    this.restApiService.getTripById(tripNumber).subscribe((res)=>{
      console.log(JSON.stringify(res));
      //Take res and work it :)
      //foreach on each station and put it on map
      //make component call here
    });

  }
}
