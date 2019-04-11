import { NgModule } from "@angular/core";
import { CommonModule } from '@angular/common';
import { GN2CommonModule } from "@geonature_common/GN2Common.module";
import { Routes, RouterModule } from "@angular/router";
import { DispositifsComponent } from "./components/dispositifs.component";
import { InfoDispositifComponent } from "./components/info.dispositif.component";

// my module routing
const routes: Routes = [
  { path: "", component: DispositifsComponent },
  { path: "infodispositif/:id", component: InfoDispositifComponent }
];

@NgModule({
  declarations: [DispositifsComponent, InfoDispositifComponent],
  imports: [GN2CommonModule, RouterModule.forChild(routes), CommonModule],
  providers: [],
  bootstrap: []
})
export class GeonatureModule { }
