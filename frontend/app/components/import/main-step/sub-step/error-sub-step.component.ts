import {Component, Input, Output, EventEmitter} from '@angular/core';
import {ErrorHistoryService} from '../../../../services/error.history.service';
import {PsdrfError, PsdrfErrorCoordinates} from '../../../../models/psdrfObject.model';


@Component({
    selector: "error-sub-step",
    templateUrl: "./error-sub-step.component.html",
    styleUrls: ["./error-sub-step.component.scss"],
  })
  export class ErrorSubStepComponent {
    value: string; //Valeur Corrigée par l'utilisateur
    selectedButtonIndex: number=0; //IndexButton Sélectionné
    modifiedIndexes: number[] = []; //liste des indexs des boutons modifiés 

    @Input() mainStepIndex: number; //Index du main step auquel le subStep appartient
    @Input() subStepIndex: number;
    @Input() psdrfError: PsdrfError;
    @Input() listCorrection: any;
    @Output() indexButtonClicked=new EventEmitter<PsdrfErrorCoordinates>();
    @Output() modificationValidated=new EventEmitter<{errorCoordinates: PsdrfErrorCoordinates[], newErrorValue: string}>();
    @Output() allRowsModified=new EventEmitter<number>();


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
      // Ajouter l'index seulement si il n'est pas déjà présent
      if(this.modifiedIndexes.indexOf(this.selectedButtonIndex) === -1){
        this.modifiedIndexes.push(this.selectedButtonIndex);
      }      
      this.modificationValidated.next({errorCoordinates: [new PsdrfErrorCoordinates(this.psdrfError.table, this.psdrfError.column, this.psdrfError.row[this.selectedButtonIndex])], newErrorValue: this.value});
      //Si tous les index ont été modifiés, l'évènement allStepsModified est lancé
      if(this.modifiedIndexes.length == this.psdrfError.row.length){
        this.allRowsModified.next(this.subStepIndex);
      }
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
      this.allRowsModified.next(this.subStepIndex);
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