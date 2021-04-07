import {Component, Output, EventEmitter } from '@angular/core';
import {CdkStepper, StepperSelectionEvent} from '@angular/cdk/stepper';

@Component({
    selector: "errortype-stepper",
    templateUrl: "./errortype-stepper.component.html",
    styleUrls: ["./errortype-stepper.component.scss"],
    // This custom stepper provides itself as CdkStepper so that it can be recognized
    // by other components.
    providers: [{ provide: CdkStepper, useExisting: ErrorTypeStepperComponent }]
  })
  export class ErrorTypeStepperComponent extends CdkStepper {
    @Output()
    selectionChange: EventEmitter<StepperSelectionEvent>

    onClick(index: number): void {
      this.selectedIndex = index;
    }
  }