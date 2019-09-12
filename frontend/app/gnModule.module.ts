import { NgModule } from "@angular/core";
import { ReactiveFormsModule } from "@angular/forms";
import { CommonModule } from '@angular/common';
import { GN2CommonModule } from "@geonature_common/GN2Common.module";
import { Routes, RouterModule } from "@angular/router";
import { DispositifsComponent } from "./components/dispositifs.component";
import { InfoDispositifComponent } from "./components/info.dispositif.component";
import { FormDispositifComponent } from "./components/form.dispositif.component";

// my module routing
const routes: Routes = [
  { path: "", component: DispositifsComponent },
  { path: "infodispositif/:id", component: InfoDispositifComponent }
];

@NgModule({
  declarations: [
    DispositifsComponent,
    InfoDispositifComponent,
    FormDispositifComponent,
  ],
  imports: [
    GN2CommonModule,
    RouterModule.forChild(routes),
    CommonModule,
    ReactiveFormsModule
  ],
  providers: [],
  bootstrap: []
})
export class GeonatureModule { }
