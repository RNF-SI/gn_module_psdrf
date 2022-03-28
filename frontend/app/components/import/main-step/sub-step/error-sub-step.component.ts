import {Component, Input, Output, EventEmitter, OnInit, ElementRef} from '@angular/core';
import {ErrorCorrectionService} from '../../../../services/error.correction.service';
import {MatTableDataSource} from '@angular/material/table';
import {PsdrfError, PsdrfErrorCoordinates} from '../../../../models/psdrfObject.model';
// import { FormArray, FormGroup, FormBuilder } from '@angular/forms';


@Component({
    selector: "error-sub-step",
    templateUrl: "./error-sub-step.component.html",
    styleUrls: ["./error-sub-step.component.scss"],
  })
  export class ErrorSubStepComponent implements OnInit{
    value: string; //Valeur Corrigée par l'utilisateur
    selectedButtonIndex: number=0; //IndexButton Sélectionné
    changedIndexes: number[] = []; //liste des indexs des boutons modifiés ou supprimés
    listCorrection: any={};
    isOptionCardDisplayed: boolean= false;
    columnToChange: string;

    @Input() mainStepIndex: number; //Index du main step auquel le subStep appartient
    @Input() subStepIndex: number; //Index du subStep 
    @Input() psdrfError: PsdrfError;
    @Input() errorType: any; 

    @Output() indexButtonClicked=new EventEmitter<PsdrfErrorCoordinates>();
    @Output() modificationValidated=new EventEmitter<{errorCoordinates: PsdrfErrorCoordinates, newErrorValue: any}>();
    @Output() allRowsModified=new EventEmitter<number>();
    @Output() applyToAllRow=new EventEmitter<{isReplacementWanted: boolean, replacingColumn: string, replacingText: string, textToReplace?: string}>();
    @Output() deletionValidated=new EventEmitter<{errorCoordinates: PsdrfErrorCoordinates}>();
    @Output() allRowsDeleted=new EventEmitter<number>();
    datasource: MatTableDataSource<any>;

    // form: FormGroup;
    textToApply: string='';
    textToReplace: string='';
    replacingText: string='';

    constructor(
      public elementRef: ElementRef,
      private correctionService: ErrorCorrectionService
    ) {
    }

    ngOnInit(){
      if(this.psdrfError.column){
        this.psdrfError.column.forEach(colName => {
          if(this.checkErrorType(colName) =="selectionError" ){
            this.listCorrection[colName]=this.correctionService.getColListCorrection(colName)
          }
        })
        this.datasource = new MatTableDataSource(this.psdrfError.value);
      }
    }


    /**
    *  Triggered when an index button is clicked:
    *  - Throw an event to inform main step
    *  - change selected button
    * @param rowIndex Index of the button (0 to nb of button -1)
    * @param row Number of the row in question 
    */
    onIndexButtonClicked(rowIndex: number, row: number): void{
      this.selectedButtonIndex = rowIndex; 
      this.indexButtonClicked.next(new PsdrfErrorCoordinates(this.psdrfError.table, this.psdrfError.column, [row]));
    }
    
    /**
    *  Triggered when a validation button is clicked:
    *  - Change Color of the button
    *  - Change selected button if necessary
    *  - Throw event if all row modified
    * @param buttonIndex Index of the validation button clicked
    */
    modifLineValidation(buttonIndex: number, newErrorValue=[this.datasource.data[buttonIndex]]): void{
      if(this.changedIndexes.indexOf(buttonIndex) === -1){
        this.changedIndexes.push(buttonIndex);
      }    
      this.modificationValidated.next({errorCoordinates: new PsdrfErrorCoordinates(this.psdrfError.table, this.psdrfError.column, [this.psdrfError.row[buttonIndex]]), newErrorValue: newErrorValue});
      if(this.changedIndexes.length == this.psdrfError.row.length){
        this.allRowsModified.next(this.subStepIndex);
      } else {
        this.selectedButtonIndex = this.selectedButtonIndex + 1; 
      }
    }

    deleteLine(buttonIndex: number): void{
      if(this.changedIndexes.indexOf(buttonIndex) === -1){
        this.changedIndexes.push(buttonIndex);
      }    
      this.deletionValidated.next({errorCoordinates: new PsdrfErrorCoordinates(this.psdrfError.table, this.psdrfError.column, [this.psdrfError.row[buttonIndex]])});
      if(this.changedIndexes.length == this.psdrfError.row.length){
        this.allRowsModified.next(this.subStepIndex);
      } else {
        this.selectedButtonIndex = this.selectedButtonIndex + 1; 
      }
    }

    displayOptions(): void{
      this.isOptionCardDisplayed = !this.isOptionCardDisplayed;
    }

    /** 
     * Fonction appelé modifie toutes les valeurs dans le subStep sélectionné
     * TODO: add in the new version
    */
    modifAllLineValidation(buttonIndex: number): void{
      this.applyToAllRow.next({isReplacementWanted: false, replacingColumn: this.columnToChange, replacingText: this.textToApply})
    }

    replaceAllLineValidation(): void{
      this.applyToAllRow.next({isReplacementWanted: true, replacingColumn: this.columnToChange, replacingText: this.replacingText, textToReplace: this.textToReplace})
    }

    /**
    *  Return true if the index correspond to the selected element or not 
    * @param rowIndex Index of a validation button 
    */
    checkSelected(rowIndex: number): boolean{
      return this.selectedButtonIndex == rowIndex;
     }

    /**
    *  Return true if a line has been modified or deleted 
    * @param rowIndex Index of a validation button
    */
    checkChanged(rowIndex: number): boolean{
      return this.changedIndexes.includes(rowIndex);
    }

  /**
  *  Return type of an error when a column name is given. Call the correctionService. 
  * @param colName Column Name
  */
    checkErrorType(psdrfCol: string): string{
      return this.correctionService.getErrorType(psdrfCol); 
    }

  /**
  *  Return the possible corrections for a column name. Call the correctionService.
  * @param colName Column Name
  */
    getColListCorrection(psdrfCol: string){
      return this.correctionService.getColListCorrection(psdrfCol)
    }
  }
