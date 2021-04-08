import {Component, Input, Output, EventEmitter } from '@angular/core';
import {CdkStepper, StepperSelectionEvent} from '@angular/cdk/stepper';

@Component({
    selector: "error-sub-stepper",
    templateUrl: "./error-sub-stepper.component.html",
    styleUrls: ["./error-sub-stepper.component.scss"],
    // This custom stepper provides itself as CdkStepper so that it can be recognized
    // by other components.
    providers: [{ provide: CdkStepper, useExisting: ErrorSubStepperComponent }]
  })
  export class ErrorSubStepperComponent extends CdkStepper {
    @Input() totallyModifiedSubStepperArr: number[]=[];

    @Output() selectionChange: EventEmitter<StepperSelectionEvent>

    onClick(index: number): void {
      this.selectedIndex = index;
    }

    /*
    Retourne si un step a été corrigé entièrement ou non
    */
    checkCorrifiedSubStepper(subStepIndex: number): boolean{
      return this.totallyModifiedSubStepperArr.includes(subStepIndex);
    }
  }