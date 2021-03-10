import { NgModule } from "@angular/core";
import { ReactiveFormsModule } from "@angular/forms";
import { CommonModule } from '@angular/common';
import { GN2CommonModule } from "@geonature_common/GN2Common.module";
import { Routes, RouterModule } from "@angular/router";
import { DispositifsComponent } from "./components/dispositifs.component";
import { InfoDispositifComponent } from "./components/info.dispositif.component";
import { FormDispositifComponent } from "./components/form.dispositif.component";
import { ImportDonneesComponent } from "./components/import.donnees.component";
import { ImportDonneesService } from "./components/import.donnees-service";
import { KeyValue, FormatNum } from "./utils";
import { DndDirective } from './directives/dnd.directive';
import { MatTableModule } from '@angular/material';

// my module routing
const routes: Routes = [
  { path: "", component: DispositifsComponent },
  { path: "infodispositif/:id", component: InfoDispositifComponent },
  { path: "importdonnees", component: ImportDonneesComponent }
];

@NgModule({
  declarations: [
    DispositifsComponent,
    InfoDispositifComponent,
    FormDispositifComponent,
    ImportDonneesComponent,
    KeyValue,
    FormatNum,
    DndDirective,
  ],
  imports: [
    GN2CommonModule,
    RouterModule.forChild(routes),
    CommonModule,
    ReactiveFormsModule,
    MatTableModule,
  ],
  providers: [
    ImportDonneesService
  ],
  bootstrap: []
})
export class GeonatureModule { }
