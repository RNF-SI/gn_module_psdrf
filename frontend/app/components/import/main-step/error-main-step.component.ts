import {Component, Input, Output, EventEmitter, ViewChild, ElementRef, AfterViewInit, OnInit} from '@angular/core';
import {StepperSelectionEvent} from '@angular/cdk/stepper';
import {ErrorHistoryService} from '../../../services/error.history.service';
import {PsdrfError, PsdrfErrorCoordinates} from '../../../models/psdrfObject.model';
import { MatStepper } from "@angular/material/stepper";


@Component({
    selector: "error-main-step",
    templateUrl: "./error-main-step.component.html",
    styleUrls: ["./error-main-step.component.scss"],
  })
export class ErrorMainStepComponent implements OnInit, AfterViewInit {
  //Indexes of the completly Modified SubStep
  totallyModifiedSubStepperArr: number[]=[];

  @Input() mainStepIndex: number;
  @Input() mainStepText: string;
  @Input() step: {'errorList': PsdrfError[], 'correctionList': any};


  @Output() subStepSelectionChange= new EventEmitter<{mainStepIndex: number, subStepIndex: number}>();
  @Output() indexButtonClicked=new EventEmitter<any>();
  @Output() modificationValidated=new EventEmitter<{errorCoordinates: {table: string, column: string[], row: number[]}, newErrorValue: any}>();
  @Output() allSubStepModified=new EventEmitter<number>();


  // SubStepper Paginator
  // Max number of steps to show at a time in view, Change this to fit your need
  MAX_STEP: number = 30;
  // Total steps included in mat-stepper in template, Change this to fit your need
  totalSteps: number =0;
  // Current page from paginator
  page: number = 0;
  // Current active step in mat-stepper
  stepIndex: number = 0;
  // Min index of step to show in view
  minStepAllowed: number = 0;
  // Max index of step to show in view
  maxStepAllowed: number = this.MAX_STEP - 1;
  // Number of total possible pages
  totalPages: number = 0;
  //Visibilité des labels du subStep
  isLabelVisible: boolean = true;


  @ViewChild('subStepper') private subStepper: MatStepper;

  @ViewChild('subStepperContainer') subStepperContainer: ElementRef;
    
  constructor(
    private historyService:ErrorHistoryService,
    private elementRef: ElementRef
  ){
  }

  ngOnInit() {
  }

  ngAfterViewInit() {
    this.totalSteps = this.step.errorList.length;
    this.totalPages = Math.ceil(this.totalSteps / this.MAX_STEP);
    this.changeMinMaxSteps(false);
  }
  
  /**
  * Triggered when a subStep button is clicked:
  * - Save the sub step in the history
  * - Throw event to display the sub step (in import component)
  * @param stepChangeEvent StepperSelectionEvent
  */
   onSubStepClicked(stepChangeEvent: StepperSelectionEvent): void{
    //Enregistrer dans l'historique à quelle étape nous en étions sur le dernier step
    this.historyService.rememberSubStep(this.step.errorList[stepChangeEvent.selectedIndex].toPsdrfErrorCoordinates(), this.mainStepIndex, stepChangeEvent.selectedIndex);
    this.subStepSelectionChange.next({mainStepIndex: this.mainStepIndex, subStepIndex: stepChangeEvent.selectedIndex});
  }

   /**
  * Triggered when a row button is clicked: 
  * - Throw event to display the line (in import component)
  * @param indexErrorCoordinates PsdrfErrorCoordinates of the line
  */
  onIndexButtonClicked(indexErrorCoordinates: PsdrfErrorCoordinates): void{
    this.indexButtonClicked.next(indexErrorCoordinates);
  }

    
    /**
  * Triggered when a modification is validated:
  * - Throw an event to display the line (in import component)
  * @param modificationErrorObj: errorCoordinates of the modificated value; newErrorValue : new value
  */
  modifValidation(modificationErrorObj: {errorCoordinates: PsdrfErrorCoordinates, newErrorValue: any}): void{
    this.modificationValidated.next(modificationErrorObj);
  }

  /** 
  * Triggered when all rows of a substep has changed :
  * - Display the next subStep
  * - Modify sub Step Appearance, adding it to totallyModifiedSubStepperArr
  * - Test if all the sub step of the main step have been changed => Throw event in this case
  * @param stepperIndex Index of the main step to change 
  */
   onAllRowsModified(stepperIndex: number){
    this.subStepper.selected.completed = true;
    this.subStepper.next();
    //ajouter seulement si non présent
    if(this.totallyModifiedSubStepperArr.indexOf(stepperIndex) === -1){
      this.totallyModifiedSubStepperArr.push(stepperIndex);
    }
    if(this.totallyModifiedSubStepperArr.length == this.step.errorList.length){
      this.allSubStepModified.next(this.mainStepIndex);
    }
  }

  /**
  * Function to test if a subStep was totally modified
  * @param subStepIndex: index of the substep
  */
  checkSubStepCompleted(subStepIndex: number): boolean{
    return this.totallyModifiedSubStepperArr.includes(subStepIndex);
  }
    //Main Paginator Functions
  /**
  * Change the page in view (next page exist)
  * @param isForward boolean. True if we go to the next page, false if we come back to the previous
  */
  pageChangeLogic(isForward = true) {
    if (this.stepIndex < this.minStepAllowed || this.stepIndex > this.maxStepAllowed) {
      if (isForward) {
        this.page++;
      } else {
        this.page--;
      }
      this.changeMinMaxSteps(isForward);
    }
  }

   /**
  * Will change min max steps allowed at any time in view
  * @param isForward boolean. True if we go to the next page, false if we come back to the previous
  */
  changeMinMaxSteps(isForward = true) {
    const pageMultiple = this.page * this.MAX_STEP;

    // maxStepAllowed will be the least value between minStep + MAX_STEP and total steps
    // minStepAllowed will be the least value between pageMultiple and maxStep - MAX_STEP
    if (pageMultiple + this.MAX_STEP - 1 <= this.totalSteps - 1) {
      this.maxStepAllowed = pageMultiple + this.MAX_STEP - 1;
      this.minStepAllowed = pageMultiple;
    } else {
      this.maxStepAllowed = this.totalSteps - 1;
      this.minStepAllowed = this.maxStepAllowed - this.MAX_STEP + 1;
    }

    // This will set the next step into view after clicking on back / next paginator arrows
    if (this.stepIndex < this.minStepAllowed || this.stepIndex > this.maxStepAllowed) {
      if (isForward) {
        this.stepIndex = this.minStepAllowed;
      } else {
        this.stepIndex = this.maxStepAllowed;
      }
      this.subStepper.selectedIndex = this.stepIndex;
    }

    this.rerender();
  }

  /**
   * Function to go back page from the current step
   */
  paginatorBack() {
    this.page--;
    this.changeMinMaxSteps(false);
  }

  /**
   * Function to go next page from the current step
   */
  paginatorNext() {
    this.page++;
    this.changeMinMaxSteps(true);
  }

  /**
   * Function to go back from the current step (change page if necessary)
   */
  goBack() {
    if (this.stepIndex > 0) {
      this.stepIndex--;
      this.subStepper.previous();
      this.pageChangeLogic(false);
    }
  }

  /**
   * Function to go forward from the current step (change page if necessary)
   */
  goForward() {
    if (this.stepIndex < this.totalSteps - 1) {
      this.stepIndex++;
      this.subStepper.next();
      this.pageChangeLogic(true);
    }
  }

  /**
   * This will display the steps in DOM based on the min max step indexes allowed in view
   */
  private rerender() {

    const headers = this.subStepperContainer.nativeElement.querySelectorAll(
      "mat-step-header"
    );
    const lines = this.subStepperContainer.nativeElement.querySelectorAll(
      ".mat-stepper-horizontal-line"
    );
    // If the step index is in between min and max allowed indexes, display it into view, otherwise set as none
    headers.forEach((h, index) => {
      if (index >= this.minStepAllowed && 
        index <= this.maxStepAllowed) {
        h.style.display = "flex";
        h.style.padding = "1px";
      } else {
        h.style.display = "none";
      }
    });

    lines.forEach((l, index) => {
      l.style.display = "none";
    });
  }

}