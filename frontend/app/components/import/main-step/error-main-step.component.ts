import {Component, Input, Output, EventEmitter, ViewChild, ElementRef, AfterViewInit, OnInit} from '@angular/core';
import {StepperSelectionEvent} from '@angular/cdk/stepper';
import {ErrorHistoryService} from '../../../services/error.history.service';
import {PsdrfError, PsdrfErrorCoordinates, PsdrfErrorCoordinates2} from '../../../models/psdrfObject.model';
import { MatStepper } from "@angular/material/stepper";


@Component({
    selector: "error-main-step",
    templateUrl: "./error-main-step.component.html",
    styleUrls: ["./error-main-step.component.scss"],
  })
export class ErrorMainStepComponent implements OnInit, AfterViewInit {
  value: string; 
  totallyModifiedSubStepperArr: number[]=[];

  @Input() mainStepIndex: number;
  @Input() mainStepText: string;
  // @Input() step: {'errorList': PsdrfError[], 'correctionList': any};
  @Input() step: any;


  @Output() subStepSelectionChange= new EventEmitter<{mainStepIndex: number, subStepIndex: number}>();
  @Output() indexButtonClicked=new EventEmitter<PsdrfErrorCoordinates>();
  @Output() indexButtonClicked2=new EventEmitter<any>();
  @Output() modificationValidated=new EventEmitter<{errorCoordinates: PsdrfErrorCoordinates[], newErrorValue: string}>();
  @Output() modificationValidated2=new EventEmitter<{errorCoordinates: {table: string, column: string[], row: number[]}, newErrorValue: any}>();
  @Output() allSubStepModified=new EventEmitter<number>();


  // SubStepper Paginator
  // Max number of steps to show at a time in view, Change this to fit your need
  MAX_STEP = 5;
  // Total steps included in mat-stepper in template, Change this to fit your need
  totalSteps =0;
  // Current page from paginator
  page = 0;
  // Current active step in mat-stepper
  stepIndex = 0;
  // Min index of step to show in view
  minStepAllowed = 0;
  // Max index of step to show in view
  maxStepAllowed = this.MAX_STEP - 1;
  // Number of total possible pages
  totalPages = 0;
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
    console.log(this.totalSteps)
    console.log(this.totalPages)
    this.changeMinMaxSteps(false);
  }
  
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

  checkSubStepCompleted(subStepIndex: number): boolean{
    return this.totallyModifiedSubStepperArr.includes(subStepIndex);
  }
    //Main Paginator Functions
  /**
   * Change the page in view
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
   * This will change min max steps allowed at any time in view
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

    console.log(
      `page: ${this.page + 1}, step: ${this.stepIndex + 1}, minStepAllowed: ${this
        .minStepAllowed + 1}, maxStepAllowed: ${this.maxStepAllowed + 1}`
    );
    this.rerender();
  }

  // /**
  //  * This will change min max steps allowed at any time in view
  //  */
  //  changeMinMaxSteps2(isForward = true) {
  //   const pageMultiple = this.page * this.MAX_STEP;

  //   // maxStepAllowed will be the least value between minStep + MAX_STEP and total steps
  //   // minStepAllowed will be the least value between pageMultiple and maxStep - MAX_STEP
  //   if (pageMultiple + this.MAX_STEP - 1 <= this.totalSteps - 1) {
  //     this.maxStepAllowed = pageMultiple + this.MAX_STEP - 1;
  //     this.minStepAllowed = pageMultiple;
  //   } else {
  //     this.maxStepAllowed = this.totalSteps - 1;
  //     this.minStepAllowed = this.maxStepAllowed - this.MAX_STEP + 1;
  //   }

  //   // This will set the next step into view after clicking on back / next paginator arrows
  //   if (this.stepIndex < this.minStepAllowed || this.stepIndex > this.maxStepAllowed) {
  //     if (isForward) {
  //       this.stepIndex = this.minStepAllowed;
  //     } else {
  //       this.stepIndex = this.maxStepAllowed;
  //     }
  //     this.subStepper.selectedIndex = this.stepIndex;
  //   }

  //   console.log(
  //     `page: ${this.page + 1}, step: ${this.stepIndex + 1}, minStepAllowed: ${this
  //       .minStepAllowed + 1}, maxStepAllowed: ${this.maxStepAllowed + 1}`
  //   );
  //   this.rerender2();
  // }

  /**
   * Function to go back a page from the current step
   */
  paginatorBack() {
    this.page--;
    this.changeMinMaxSteps(false);
  }

  /**
   * Function to go next a page from the current step
   */
  paginatorNext() {
    this.page++;
    this.changeMinMaxSteps(true);
  }

  /**
   * Function to go back from the current step
   */
  goBack() {
    if (this.stepIndex > 0) {
      this.stepIndex--;
      this.subStepper.previous();
      this.pageChangeLogic(false);
    }
  }

  /**
   * Function to go forward from the current step
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
    // console.log(this.contentPlaceholder.nativeElement)
    //setTimeout(() => {console.log(this.contentPlaceholder.nativeElement)})

    const headers = this.subStepperContainer.nativeElement.querySelectorAll(
      "mat-step-header"
    );
    // console.log(headers)

    const lines = this.subStepperContainer.nativeElement.querySelectorAll(
      ".mat-stepper-horizontal-line"
    );
    console.log(headers)
    console.log(lines)


    // If the step index is in between min and max allowed indexes, display it into view, otherwise set as none
    headers.forEach((h, index) => {
      console.log(index)
      if (index >= this.minStepAllowed && 
        index <= this.maxStepAllowed) {
        h.style.display = "flex";
        h.style.padding = "1px";
      } else {
        h.style.display = "none";
      }
    });

    // If the line index is between min and max allowed indexes, display it in view, otherwise set as none
    // One thing to note here: length of lines is 1 less than length of headers
    // For eg, if there are 8 steps, there will be 7 lines joining those 8 steps
    lines.forEach((l, index) => {
      l.style.display = "none";
      // console.log(index)
      // if (index >= this.minStepAllowed && 
      //   index <= this.maxStepAllowed) {
      //   l.style.display = "block";
      // } else {
      //   l.style.display = "none";
      // }
    });
  }

  // private rerender2() {
  //   // console.log(this.contentPlaceholder.nativeElement)
  //   //setTimeout(() => {console.log(this.contentPlaceholder.nativeElement)})

  //   const headers = this.subStepperContainer.nativeElement.querySelectorAll(
  //     "mat-step-header"
  //   );
  //   // console.log(headers)

  //   const lines = this.subStepperContainer.nativeElement.querySelectorAll(
  //     ".mat-stepper-horizontal-line"
  //   );

  //   console.log(headers)
  //   console.log(lines)


  //   // If the step index is in between min and max allowed indexes, display it into view, otherwise set as none
  //   headers.forEach((h, index) => {
  //     console.log(index)
  //     if (index >= this.minStepAllowed && 
  //       index <= this.maxStepAllowed) {
  //       h.style.display = "flex";
  //       h.style.padding = "24px 1px";
  //     } else {
  //       h.style.display = "none";
  //     }
  //   });

  //   // If the line index is between min and max allowed indexes, display it in view, otherwise set as none
  //   // One thing to note here: length of lines is 1 less than length of headers
  //   // For eg, if there are 8 steps, there will be 7 lines joining those 8 steps
  //   lines.forEach((l) => {
  //     l.style.display = "none";
  //   });

  // }

  // showStepLabels(){
  //   this.isLabelVisible = !this.isLabelVisible;
  //   if(this.isLabelVisible){
  //     // document.body.style.setProperty('--displayLabel', 'none')
  //     this.MAX_STEP = 5;
  //   } else {
  //     // document.body.style.setProperty('--displayLabel', 'none')
  //     this.MAX_STEP = 60; 
  //   }
  //   this.totalPages = Math.ceil(this.totalSteps / this.MAX_STEP);
  //   // this.minStepAllowed = 0;
  //   // this.maxStepAllowed = this.MAX_STEP - 1;
  //   this.page =Math.trunc(this.stepIndex / this.MAX_STEP);
    
  //   if(this.isLabelVisible){
  //     this.changeMinMaxSteps(false);
  //     const labels = this.subStepperContainer.nativeElement.querySelectorAll(
  //       ".mat-step-label"
  //     );
  //     labels.forEach((l) => {
  //       l.style.display = "flex";
  //     });
  //   } else {
  //     this.changeMinMaxSteps2(false);
  //     const labels = this.subStepperContainer.nativeElement.querySelectorAll(
  //       ".mat-step-label"
  //     );
  //     labels.forEach((l) => {
  //       l.style.display = "none";
  //     });
  //   }
  //   // this.changeDetector.detectChanges();
  // }

}