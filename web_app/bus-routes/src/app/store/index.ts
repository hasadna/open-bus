import {
  ActionReducer,
  ActionReducerMap,
  createFeatureSelector,
  createSelector,
  MetaReducer
} from '@ngrx/store';
import { environment } from '../../environments/environment';
import { IAppState } from 'src/app/store/states/app.state';
import { tripReducers } from 'src/app/store/reducers/trip.reducers';
//import { busStopReducers } from 'src/app/store/reducers/bus-stop.reducers';

export interface State {

}

export const reducers: ActionReducerMap<IAppState, any> = {
  trips: tripReducers
  //stops: busStopReducers
};

export const metaReducers: MetaReducer<State>[] = !environment.production ? [] : [];
