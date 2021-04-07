import {Component, Input, Output, EventEmitter} from '@angular/core';
import {ErrorHistoryService} from '../../../../services/error.history.service';
import {PsdrfError, PsdrfErrorCoordinates} from '../../../../models/psdrfObject.model';


@Component({
    selector: "error-sub-step",
    templateUrl: "./error-sub-step.component.html",
    styleUrls: ["./error-sub-step.component.scss"],
  })
  export class ErrorSubStepComponent {
    value: string; 
    selectedButtonIndex: number=0;
    modifiedIndexes: number[] = [];

    @Input() mainStepIndex: number;
    @Input() subStepIndex: number;
    @Input() psdrfError: PsdrfError;
    @Input() listCorrection: any;
    @Output() indexButtonClicked=new EventEmitter<PsdrfErrorCoordinates>();
    @Output() modificationValidated=new EventEmitter<{errorCoordinates: PsdrfErrorCoordinates[], newErrorValue: string}>();

    constructor(private historyService:ErrorHistoryService){}

    /*
      Fonction appelée lorsqu'un index button est cliqué
    */
    onIndexButtonClicked(rowIndex: number, row: number): void{
      this.historyService.rememberIndex(this.psdrfError.toPsdrfErrorCoordinates(rowIndex), rowIndex, this.mainStepIndex, this.subStepIndex);
      this.selectedButtonIndex = rowIndex; 
      this.indexButtonClicked.next(new PsdrfErrorCoordinates(this.psdrfError.table, this.psdrfError.column, row));
    }
    
    /*
      Fonction qui modifie une seule valeur
    */
    modifValidation(): void{
      this.modifiedIndexes.push(this.selectedButtonIndex);
      this.modificationValidated.next({errorCoordinates: [new PsdrfErrorCoordinates(this.psdrfError.table, this.psdrfError.column, this.psdrfError.row[this.selectedButtonIndex])], newErrorValue: this.value});
    }

    /*
      Fonction appelé modifie toutes les valeurs dans le subStep sélectionné
    */
    modifValidationAll(): void{
      this.modifiedIndexes= Array.from(Array(this.psdrfError.row.length).keys());
      let psdrfErrorCoorArray: PsdrfErrorCoordinates[]=[];
      this.psdrfError.row.forEach(row => {
        psdrfErrorCoorArray.push(new PsdrfErrorCoordinates(this.psdrfError.table, this.psdrfError.column, row));
      })
      this.modificationValidated.next({errorCoordinates: psdrfErrorCoorArray, newErrorValue: this.value});
    }
  
    /*
      Fonction qui retourne si un index correspond à celui de l'élement sélectionné ou non
    */
    checkSelected(rowIndex: number): boolean{
      return this.selectedButtonIndex == rowIndex;
     }

    /*
      Fonction qui retourne si un index correspond à celui d'un élément modifié ou non
    */
    checkModified(rowIndex: number): boolean{
      return this.modifiedIndexes.includes(rowIndex);
    }
  }