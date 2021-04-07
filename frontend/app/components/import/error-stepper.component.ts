import {Component, Output, EventEmitter } from '@angular/core';
import {CdkStepper, StepperSelectionEvent} from '@angular/cdk/stepper';

@Component({
    selector: "error-stepper",
    templateUrl: "./error-stepper.component.html",
    styleUrls: ["./error-stepper.component.scss"],
    // This custom stepper provides itself as CdkStepper so that it can be recognized
    // by other components.
    providers: [{ provide: CdkStepper, useExisting: ErrorStepperComponent }]
  })
  export class ErrorStepperComponent extends CdkStepper {
    @Output()
    selectionChange: EventEmitter<StepperSelectionEvent>

    onClick(index: number): void {
      this.selectedIndex = index;
    }
  }