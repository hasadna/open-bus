import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { MapCompComponent } from './components/map-comp/map-comp.component';
import { PageNotFoundComponent } from './components/page-not-found/page-not-found.component';
import { HttpClientModule } from  '@angular/common/http';

const routes: Routes = [
  { path: 'busmap', component: MapCompComponent },
  { path: '**', component: PageNotFoundComponent }
];


@NgModule({
  imports: [
    RouterModule.forRoot(routes),
    HttpClientModule
  ],
  exports: [RouterModule]
})
export class AppRoutingModule { }
