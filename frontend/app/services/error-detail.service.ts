import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class ErrorDetailService {
  private errorSource = new BehaviorSubject<any | null>(null);
  currentError = this.errorSource.asObservable();

  constructor() {}

  changeErrorDetail(error: any) {
    this.errorSource.next(JSON.parse(error));
  }
}
