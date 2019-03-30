import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { MapCompComponent } from './components/map-comp/map-comp.component';
import { PageNotFoundComponent } from './components/page-not-found/page-not-found.component';
import { LeafletModule } from '@asymmetrik/ngx-leaflet';

import { RestApiService } from './services/rest-api/rest-api.service';
import { MapMngrService } from 'src/app/services/map-mngr/map-mngr.service';

import { StoreModule } from '@ngrx/store';
import { reducers, metaReducers } from './store';
import { EffectsModule } from '@ngrx/effects';
import { AppEffects } from './app.effects';

@NgModule({
  declarations: [
    AppComponent,
    MapCompComponent,
    PageNotFoundComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    LeafletModule.forRoot(),
    StoreModule.forRoot(reducers, { metaReducers }),
    EffectsModule.forRoot([AppEffects])
  ],
  providers: [
    RestApiService,
    MapMngrService
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
