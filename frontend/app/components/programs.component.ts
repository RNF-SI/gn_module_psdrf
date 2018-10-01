import { Component, OnInit } from "@angular/core";
import { HttpClient } from '@angular/common/http';
import { AppConfig } from '@geonature_config/app.config';


@Component({
  selector: "pnx-cmr-programs",
  templateUrl: "programs.component.html"
})
export class ProgramsComponent implements OnInit {
  public programs: Array<any>;
  constructor(private _api: HttpClient) { }

  ngOnInit() {
    this._api.get<any>(`${AppConfig.API_ENDPOINT}/cmr/programs`)
      .subscribe(data => {
        this.programs = data;
        console.log(data);
      })

  }
}
