import {Component, Input, Output, EventEmitter, OnInit} from '@angular/core';
import {ErrorHistoryService} from '../../../../services/error.history.service';
import {MatTableDataSource} from '@angular/material/table';
import {PsdrfError, PsdrfErrorCoordinates, PsdrfErrorCoordinates2} from '../../../../models/psdrfObject.model';
// import { FormArray, FormGroup, FormBuilder } from '@angular/forms';


@Component({
    selector: "error-sub-step",
    templateUrl: "./error-sub-step.component.html",
    styleUrls: ["./error-sub-step.component.scss"],
  })
  export class ErrorSubStepComponent implements OnInit{
    value: string; //Valeur Corrigée par l'utilisateur
    selectedButtonIndex: number=0; //IndexButton Sélectionné
    modifiedIndexes: number[] = []; //liste des indexs des boutons modifiés 

    @Input() mainStepIndex: number; //Index du main step auquel le subStep appartient
    @Input() subStepIndex: number;
    @Input() psdrfError: any;
    @Input() listCorrection: any;
    @Input() errorType: any; 
    @Output() indexButtonClicked=new EventEmitter<PsdrfErrorCoordinates>();
    @Output() indexButtonClicked2=new EventEmitter<PsdrfErrorCoordinates2>();
    @Output() modificationValidated=new EventEmitter<{errorCoordinates: PsdrfErrorCoordinates[], newErrorValue: string}>();
    @Output() modificationValidated2=new EventEmitter<{errorCoordinates: PsdrfErrorCoordinates2, newErrorValue: any}>();
    @Output() allRowsModified=new EventEmitter<number>();
    datasource: any;

    // form: FormGroup;


    constructor(
      private historyService:ErrorHistoryService,
      ) {
  
    }

    ngOnInit(){
      console.log(this.psdrfError)
      this.datasource = new MatTableDataSource(this.psdrfError.value);
    }


    /*
      Fonction appelée lorsqu'un index button est cliqué
    */
    onIndexButtonClicked(rowIndex: number, row: number): void{
      // console.log(this.psdrfError)
      // this.historyService.rememberIndex(this.psdrfError.toPsdrfErrorCoordinates(rowIndex), rowIndex, this.mainStepIndex, this.subStepIndex);
      // this.selectedButtonIndex = rowIndex; 
      // this.indexButtonClicked.next(new PsdrfErrorCoordinates(this.psdrfError.table, this.psdrfError.column, row));
    }

    onIndexButtonClicked2(rowIndex: number, row: number): void{
      // console.log(this.psdrfError)
      // this.historyService.rememberIndex(this.psdrfError.toPsdrfErrorCoordinates(rowIndex), rowIndex, this.mainStepIndex, this.subStepIndex);
      // this.selectedButtonIndex = rowIndex; 
      this.historyService.rememberIndex2(this.psdrfError.toPsdrfErrorCoordinates2(), rowIndex, this.mainStepIndex, this.subStepIndex);
      this.selectedButtonIndex = rowIndex; 
      this.indexButtonClicked2.next(new PsdrfErrorCoordinates2(this.psdrfError.table, this.psdrfError.column, [row]));
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

    modifValidation2(): void{
      console.log(this.datasource)
      if(this.modifiedIndexes.indexOf(this.selectedButtonIndex) === -1){
        this.modifiedIndexes.push(this.selectedButtonIndex);
      }    
      this.modificationValidated2.next({errorCoordinates: new PsdrfErrorCoordinates2(this.psdrfError.table, this.psdrfError.column, this.psdrfError.row), newErrorValue: this.datasource.data});
      if(this.modifiedIndexes.length == this.psdrfError.row.length){
        this.allRowsModified.next(this.subStepIndex);
      }
    }

    deleteRow(rowIndex): void{
      console.log(rowIndex);
      console.log(this.datasource);
      this.psdrfError.row.splice(rowIndex, 1);

      this.datasource.data.splice(rowIndex, 1);
      this.datasource._updateChangeSubscription();
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