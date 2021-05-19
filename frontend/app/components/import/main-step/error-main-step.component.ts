import {Component, Input, Output, EventEmitter} from '@angular/core';
import {StepperSelectionEvent} from '@angular/cdk/stepper';
import {ErrorHistoryService} from '../../../services/error.history.service';
import {PsdrfError, PsdrfErrorCoordinates, PsdrfErrorCoordinates2} from '../../../models/psdrfObject.model';


@Component({
    selector: "error-main-step",
    templateUrl: "./error-main-step.component.html",
    styleUrls: ["./error-main-step.component.scss"],
  })
  export class ErrorMainStepComponent {
    value: string; 
    totallyModifiedSubStepperArr: number[]=[];

    @Input() mainStepIndex: number;
    // @Input() step: {'errorList': PsdrfError[], 'correctionList': any};
    @Input() step: any;


    @Output() subStepSelectionChange= new EventEmitter<{mainStepIndex: number, subStepIndex: number}>();
    @Output() indexButtonClicked=new EventEmitter<PsdrfErrorCoordinates>();
    @Output() indexButtonClicked2=new EventEmitter<any>();
    @Output() modificationValidated=new EventEmitter<{errorCoordinates: PsdrfErrorCoordinates[], newErrorValue: string}>();
    @Output() modificationValidated2=new EventEmitter<{errorCoordinates: {table: string, column: string[], row: number[]}, newErrorValue: any}>();
    @Output() allSubStepModified=new EventEmitter<number>();
    
    constructor(private historyService:ErrorHistoryService){}

    /*
      Fonction qui est appelée lorsqu'un bouton subStep est cliqué
    */
    onSubStepClicked(stepChangeEvent: StepperSelectionEvent): void{
      //Enregistrer dans l'historique à quelle étape nous en étions sur le dernier step
      this.historyService.rememberSubStep(stepChangeEvent.selectedIndex, this.step.errorList[stepChangeEvent.selectedIndex].toPsdrfErrorCoordinates(0), this.mainStepIndex);
      this.subStepSelectionChange.next({mainStepIndex: this.mainStepIndex, subStepIndex: stepChangeEvent.selectedIndex});
    }

    onSubStepClicked2(stepChangeEvent: StepperSelectionEvent): void{
      //Enregistrer dans l'historique à quelle étape nous en étions sur le dernier step
      this.historyService.rememberSubStep(stepChangeEvent.selectedIndex, this.step.errorList[stepChangeEvent.selectedIndex].toPsdrfErrorCoordinates2(), this.mainStepIndex);
      this.subStepSelectionChange.next({mainStepIndex: this.mainStepIndex, subStepIndex: stepChangeEvent.selectedIndex});
    }

    /*
      Fonction qui est appelée lorsqu'un bouton index de ligne est cliqué
    */
    onIndexButtonClicked(indexErrorCoordinates: PsdrfErrorCoordinates): void{
      this.indexButtonClicked.next(indexErrorCoordinates);
    }
    onIndexButtonClicked2(indexErrorCoordinates: PsdrfErrorCoordinates2): void{
      this.indexButtonClicked2.next(indexErrorCoordinates);
    }

    
    /*
      Fonction qui est appelée lorsqu'on valide la modification d'une valeur
    */
    modifValidation(modificationErrorObj: {errorCoordinates: PsdrfErrorCoordinates[], newErrorValue: string}): void{
      this.modificationValidated.next(modificationErrorObj);
    }

    modifValidation2(modificationErrorObj: {errorCoordinates: PsdrfErrorCoordinates2, newErrorValue: any}): void{
      this.modificationValidated2.next(modificationErrorObj);
    }


    /*
      Fonction modifiant l'apparence des stepper lorsque ceux-ci ont été complètement modifiés
    */
    modifySteppersAppearance(stepperIndex: number){
      //ajouter seulement si non présent
      if(this.totallyModifiedSubStepperArr.indexOf(stepperIndex) === -1){
        this.totallyModifiedSubStepperArr.push(stepperIndex);
      }
      if(this.totallyModifiedSubStepperArr.length == this.step.errorList.length){
        this.allSubStepModified.next(this.mainStepIndex);
      }
    }

  }