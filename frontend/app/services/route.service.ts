import { Injectable } from "@angular/core";
import { HttpClient, HttpParams } from "@angular/common/http";

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
    const httpOptions = {
      headers: { 'Content-Type': 'application/json' },
    };
    return this._http.post<any>(
      `${AppConfig.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/integration`,
      data,
      httpOptions
    ); 
  }

  psdrf_data_analysis(test) {
    console.log("fsfdsdg")
    return this._http.post<any>(
      `${AppConfig.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/analysis`,
      test
    );
  }

}
