import { Injectable } from "@angular/core";
import { Observable } from 'rxjs';
import { HttpClient, HttpHeaders, HttpParams } from "@angular/common/http";

import { AppConfig } from "@geonature_config/app.config";
import { ModuleConfig } from "../module.config";

@Injectable()
export class PsdrfDataService {
  constructor(
    private _http: HttpClient,
  ) {}

  psdrf_data_verification(data) {
    const httpOptions = {
      headers: { 'Content-Type': 'application/json' },
    };
    return this._http.post<any>(
      `${AppConfig.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/validation`,
      data,
      httpOptions
    );
  }

  psdrf_data_verification_with_shape(excelAndShapeData) {
    return this._http.post<any>(
      `${AppConfig.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/shapeValidation`,
      excelAndShapeData
    );
  }

  psdrfIntegrationToDatabase(data){
    return this._http.post<any>(
      `${AppConfig.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/integration`,
      data
    ); 
  }

  psdrf_data_analysis(id: number) {
    const headers = new HttpHeaders({ 'Content-Type': 'application/json', responseType : 'blob'});

    let url = `${AppConfig.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/analysis/`+ id

    return this._http.get(
      url, 
      { observe: "response", headers : headers, responseType : 'blob' }
      )
      .map((res) => {
        let data = {
                      pdf: new Blob([res.body], {type: res.headers.get('Content-Type')}),
                      filename: res.headers.get('filename')
                    }
        return data ;
      }).catch((err) => {
        return Observable.throw(err);
      });
    
  }

}
