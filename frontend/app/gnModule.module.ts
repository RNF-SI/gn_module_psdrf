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
import { AdminTableComponent } from "./reusable-components/admin-table/admin-table.component";
import { AdminComponent } from "./components/admin/admin.component";
import { ExcelImportService } from "./services/excel.import.service";
import { PsdrfDataService } from "./services/route.service";
import { ErrorHistoryService } from "./services/error.history.service";
import { ErrorCorrectionService } from "./services/error.correction.service";
import { SharedService } from "./services/shared.service";
import { KeyValue, FormatNum } from "./utils";
import { DndDirective } from './directives/dnd.directive';
import { MatTableModule } from '@angular/material/table';
import { MatSnackBarModule } from '@angular/material/snack-bar'; 
import { CdkStepperModule } from '@angular/cdk/stepper';
import {MatCheckboxModule} from '@angular/material/checkbox'; 

// my module routing
const routes: Routes = [
  { path: "", component: DispositifsComponent },
  { path: "infodispositif/:id", component: InfoDispositifComponent },
  { path: "importdonnees", component: ImportDonneesComponent },
  { path: "adminPage", component: AdminComponent }
];

@NgModule({
  declarations: [
    DispositifsComponent,
    InfoDispositifComponent,
    FormDispositifComponent,
    ImportDonneesComponent,
    AdminComponent,
    KeyValue,
    FormatNum,
    DndDirective,
    ErrorMainStepComponent,
    ErrorSubStepComponent,
    AdminTableComponent
  ],
  imports: [
    GN2CommonModule,
    RouterModule.forChild(routes),
    CommonModule,
    ReactiveFormsModule,
    MatTableModule,
    MatSnackBarModule,
    CdkStepperModule,
    MatCheckboxModule
  ],
  providers: [
    ExcelImportService,
    PsdrfDataService,
    ErrorHistoryService, 
    ErrorCorrectionService, 
    SharedService
  ],
  bootstrap: []
})
export class GeonatureModule { }
