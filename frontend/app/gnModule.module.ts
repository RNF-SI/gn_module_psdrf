import { NgModule } from "@angular/core";
import { ReactiveFormsModule } from "@angular/forms";
import { CommonModule } from '@angular/common';
import { GN2CommonModule } from "@geonature_common/GN2Common.module";
import { Routes, RouterModule } from "@angular/router";
import { DispositifsComponent } from "./components/dispositifs.component";
import { InfoDispositifComponent } from "./components/info.dispositif.component";
import { FormDispositifComponent } from "./components/form.dispositif.component";
import { ImportDonneesComponent } from "./components/import/import.donnees.component";
import { ErrorTypeStepperComponent } from "./components/import/errortype-stepper.component";
import { ErrorTypeStepComponent } from "./components/import/errortype-step.component";
import { ErrorStepperComponent } from "./components/import/error-stepper.component";
import { ErrorStepComponent } from "./components/import/error-step.component";
import { ExcelImportService } from "./services/excel.import.service";
import { PsdrfDataService } from "./services/route.service";
import { ErrorHistoryService } from "./services/error.history.service";
import { KeyValue, FormatNum } from "./utils";
import { DndDirective } from './directives/dnd.directive';
import { MatTableModule } from '@angular/material';
import { CdkStepperModule } from '@angular/cdk/stepper';

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
    ErrorTypeStepperComponent,
    ErrorTypeStepComponent,
    ErrorStepperComponent,
    ErrorStepComponent
  ],
  imports: [
    GN2CommonModule,
    RouterModule.forChild(routes),
    CommonModule,
    ReactiveFormsModule,
    MatTableModule,
    CdkStepperModule,
  ],
  providers: [
    ExcelImportService,
    PsdrfDataService,
    ErrorHistoryService
  ],
  bootstrap: []
})
export class GeonatureModule { }
