import { NgModule } from "@angular/core";
import { ReactiveFormsModule } from "@angular/forms";
import { CommonModule } from '@angular/common';
import { GN2CommonModule } from "@geonature_common/GN2Common.module";
import { Routes, RouterModule } from "@angular/router";
import { DispositifsComponent } from "./components/dispositifs.component";
import { InfoDispositifComponent } from "./components/info.dispositif.component";
import { FormDispositifComponent } from "./components/form.dispositif.component";
import { ImportDonneesComponent } from "./components/import/import.donnees.component";
import { ErrorMainStepComponent } from "./components/import/main-step/error-main-step.component";
import { ErrorSubStepComponent } from "./components/import/main-step/sub-step/error-sub-step.component";
import { ExcelImportService } from "./services/excel.import.service";
import { PsdrfDataService } from "./services/route.service";
import { ErrorHistoryService } from "./services/error.history.service";
import { ErrorCorrectionService } from "./services/error.correction.service";
import { KeyValue, FormatNum } from "./utils";
import { DndDirective } from './directives/dnd.directive';
import { MatTableModule } from '@angular/material';
import { MatSnackBarModule } from '@angular/material'; 
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
    ErrorMainStepComponent,
    ErrorSubStepComponent
  ],
  imports: [
    GN2CommonModule,
    RouterModule.forChild(routes),
    CommonModule,
    ReactiveFormsModule,
    MatTableModule,
    MatSnackBarModule,
    CdkStepperModule,
  ],
  providers: [
    ExcelImportService,
    PsdrfDataService,
    ErrorHistoryService, 
    ErrorCorrectionService
  ],
  bootstrap: []
})
export class GeonatureModule { }
