import {Component, Output, Input, EventEmitter } from '@angular/core';
import {CdkStepper, StepperSelectionEvent} from '@angular/cdk/stepper';

@Component({
    selector: "error-main-stepper",
    templateUrl: "./error-main-stepper.component.html",
    styleUrls: ["./error-main-stepper.component.scss"],
    // This custom stepper provides itself as CdkStepper so that it can be recognized
    // by other components.
    providers: [{ provide: CdkStepper, useExisting: ErrorMainStepperComponent }]
  })
  export class ErrorMainStepperComponent extends CdkStepper {
    @Input() totallyModifiedMainStepperArr: number[]=[];

    @Output()
    selectionChange: EventEmitter<StepperSelectionEvent>

    onClick(index: number): void {
      this.selectedIndex = index;
    }

    checkCorrifiedSubStepper(subStepIndex: number): boolean{
      return this.totallyModifiedMainStepperArr.includes(subStepIndex);
    }
  }