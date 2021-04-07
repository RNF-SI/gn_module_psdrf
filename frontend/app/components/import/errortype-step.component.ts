import {Component, Input, Output, EventEmitter} from '@angular/core';
import {StepperSelectionEvent} from '@angular/cdk/stepper';
import {ErrorHistoryService} from '../../services/error.history.service';
import {PsdrfError, PsdrfErrorCoordinates} from '../../models/psdrfObject.model';


@Component({
    selector: "errortype-step",
    templateUrl: "./errortype-step.component.html",
    styleUrls: ["./errortype-step.component.scss"],
  })
  export class ErrorTypeStepComponent {
    value: string; 

    @Input() errorTypeIndex: number;
    @Input() step: {'errorList': PsdrfError[], 'correctionList': any};

    @Output() subStepSelectionChange= new EventEmitter<{errorTypeIndex: number, selectedIndex: number}>();
    @Output() indexButtonClicked=new EventEmitter<PsdrfErrorCoordinates>();
    @Output() modificationValidated=new EventEmitter<{errorCoordinates: PsdrfErrorCoordinates[], newErrorValue: string}>();

    constructor(private historyService:ErrorHistoryService){}

    /*
      Fonction qui est appelée lorsqu'un bouton subStep est cliqué
    */
    onSubStepClicked(stepChangeEvent: StepperSelectionEvent): void{
      //Enregistrer dans l'historique à quelle étape nous en étions sur le dernier step
      this.historyService.rememberSubStep(stepChangeEvent.selectedIndex, this.step.errorList[stepChangeEvent.selectedIndex].toPsdrfErrorCoordinates(0), this.errorTypeIndex);
      this.subStepSelectionChange.next({errorTypeIndex: this.errorTypeIndex, selectedIndex: stepChangeEvent.selectedIndex});
    }

    /*
      Fonction qui est appelée lorsqu'un bouton index de ligne est cliqué
    */
    onIndexButtonClicked(indexErrorCoordinates: PsdrfErrorCoordinates): void{
      this.indexButtonClicked.next(indexErrorCoordinates);
    }
    
    /*
      Fonction qui est appelée lorsqu'on valide la modification d'une valeur
    */
    modifValidation(modificationErrorObj: {errorCoordinates: PsdrfErrorCoordinates[], newErrorValue: string}): void{
      this.modificationValidated.next(modificationErrorObj);
    }

  }