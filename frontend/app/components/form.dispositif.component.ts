import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
// import { ActivatedRoute, Router, ParamMap } from "@angular/router";
import { HttpClient } from '@angular/common/http';
import { AppConfig } from '@geonature_config/app.config';


@Component({
    selector: 'rnf-psdrf-form-dispositif',
    templateUrl: 'form.dispositif.component.html'
})
export class FormDispositifComponent implements OnInit {
    @Input() public dispositif: any;
    @Output() public saved = new EventEmitter<boolean>();
    @Output() public canceled = new EventEmitter<boolean>();

    public organismes: object[];

    public dispositifForm = new FormGroup({
        name: new FormControl(''),
        id_organisme: new FormControl()
    });

    public dispositifEndPoint: string = "psdrf/dispositif";
    public dispositifSaveEndPoint: string = "psdrf/saveDispositif"
    public organismsEndPoint: string = "users/organisms"

    constructor(
        private _api: HttpClient
      ) { }

    ngOnInit() {
      this._api.get<any>(`${AppConfig.API_ENDPOINT}/${this.organismsEndPoint}`)
          .subscribe(data => {
              this.organismes = data;
            });

      interface formInterface {
        name?: any,
        id_organisme?: any
      }
      let formData: formInterface;


      formData = {name: this.dispositif.name};
      if (this.dispositif.organisme !== undefined) {
        formData.id_organisme = this.dispositif.organisme.id_organisme;
      }
      this.dispositifForm.patchValue(formData);
    }

    onSubmit() {
        let data = this.dispositifForm.value;
        data.id = this.dispositif.id;
        this._api.post<any>(`${AppConfig.API_ENDPOINT}/${this.dispositifSaveEndPoint}`, data)
          .subscribe(data => {
            if (data.success) {
              console.log("bien enregistré !");
              this.saved.emit(true);
            }
          });
    }

    onCancel() {
      // form canceled
      this.canceled.emit(true);
    }
}