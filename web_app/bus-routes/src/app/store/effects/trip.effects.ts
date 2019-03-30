import { Injectable } from "@angular/core/src/di/injectable";
import { Effect, ofType, Actions } from '@ngrx/effects';
import { Store, select } from '@ngrx/store';
import { of } from 'rxjs';
import { switchMap, map, withLatestFrom } from 'rxjs/operators'
import { MapMngrService } from 'src/app/services/map-mngr/map-mngr.service';
import { IAppState } from 'src/app/store/states/app.state';
import { TripGetAction, ETripActions, TripGetActionSuccess } from 'src/app/store/actions/trip.action';
import { Trip } from 'src/app/data/trip';

@Injectable()
export class TripEffects {
  @Effect()
  getTrip$ = this._actions$.pipe(
    ofType<TripGetAction>(ETripActions.GET_TRIP),
    switchMap(() => this._mapMngrService.loadTrip(1/*action.payload*/)),
    switchMap((tripHttp: Trip) => {
       return of(new TripGetActionSuccess(tripHttp));
    })
  );

  constructor(
    private _mapMngrService: MapMngrService,
    private _actions$: Actions,
    //private _store: Store<IAppState>
  ){}
}
