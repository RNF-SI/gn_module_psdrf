import { Component, OnInit } from '@angular/core';
import { ToastrService, ToastPackage } from 'ngx-toastr';
import { Toast } from 'ngx-toastr';

import { ErrorDetailService } from '../../services/error-detail.service'; // replace with the actual path to your service
import { Clipboard } from '@angular/cdk/clipboard';

@Component({
  selector: 'custom-toast',
  templateUrl: 'custom-toast.component.html',
  styleUrls: ['custom-toast.component.scss'],
})
export class CustomToastComponent extends Toast implements OnInit {
  success: string = '';
  message: string = '';
  errorDetail: string = '';
  showErrorDetail: boolean = false;
  detailSnippet: string = '';

  constructor(
    protected toastrService: ToastrService,
    public toastPackage: ToastPackage,
    private errorDetailService: ErrorDetailService,
    private clipboard: Clipboard,
  ) {
    super(toastrService, toastPackage);
  }

  ngOnInit() {

    this.errorDetailService.currentError.subscribe(error => {
      if (error) {
        this.success = error.success;
        this.message = error.message;      
        this.errorDetail = error.error_detail;
        this.detailSnippet = this.errorDetail.slice(0, 300) + ' [......]';
      }
    });
  }

  seeDetails(event: Event) {
    if(this.showErrorDetail) {
      this.showErrorDetail = false; 
    } else {
      event.preventDefault();
      console.log(this.errorDetail); // Log the full error message.
      this.showErrorDetail = true; 
    }
  }

  copyDetails(event: Event) {
    event.preventDefault();
    this.clipboard.copy(this.errorDetail);
  }

}
