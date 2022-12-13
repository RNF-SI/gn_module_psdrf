import { Injectable } from "@angular/core";
import { Observable } from 'rxjs';
import { HttpClient, HttpHeaders, HttpParams } from "@angular/common/http";

import { AppConfig } from "@geonature_config/app.config";
import { ModuleConfig } from "../module.config";
import { map } from 'rxjs/operators';

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

  psdrf_data_analysis(id: number, isCarnetToDownload: boolean, isPlanDesArbresToDownload: boolean, parameters: {name: string, text: string, value: any}[] ) {
    const headers = new HttpHeaders({ 'Content-Type': 'application/json', responseType : 'blob'});

    let url = `${AppConfig.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/analysis/`+ id
    let params = new HttpParams().set("isCarnetToDownload",isCarnetToDownload.toString()).set("isPlanDesArbresToDownload",isPlanDesArbresToDownload.toString())
    //Ajouter les paramètres relatifs à la génération des documents
    parameters.forEach(param => {
      params= params.append(param.name, param.value.toString());
    })

    return this._http.get(
      url, 
      { observe: "response", headers : headers, params: params, responseType : 'blob' }
      )
      .pipe(
        map((res) => {
          let data = {
                        zip: new Blob([res.body], {type: res.headers.get('Content-Type')}),
                        filename: res.headers.get('filename')
                      }
          return data ;
        })

      )
      .catch((err) => {
        return Observable.throw(err);
      });
    
  }

  getDispositifList(){
    return this._http.get<any>(
      `${AppConfig.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/dispositifsList`
    );
  }

  getUtilisateurAndGroupsList(){
    return this._http.get<any>(
      `${AppConfig.API_ENDPOINT}/users/roles`

      );
  }

  getUtilisateurList(){
    return this._http.get<any>(
      `${AppConfig.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/users`
      );
  }

  getGroupeList(){
    return this._http.get<any>(
      `${AppConfig.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/groups`
      );
  }

  getOrganismeList(){
    return this._http.get<any>(
      `${AppConfig.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/listOrganism`

      );
  }

  getUserGroups(userId: number){
    return this._http.get<any>(
      `${AppConfig.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/groupList/`+ userId

      );
  }

  addCorDispRole(data){
    return this._http.post<any>(
      `${AppConfig.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/corDispositifRole`,
      data
    );
  }

  updateCorDispRole(data){
    return this._http.put<any>(
      `${AppConfig.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/corDispositifRole`,
      data
    );
  }

  deleteCorDispRole(data){
     const options = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
      }),
      body: {
        "id_dispositif":  data.id_dispositif,
        "id_role": data.id_utilisateur,
      },
    };

    return this._http.delete<any>(
      `${AppConfig.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/corDispositifRole`,
      options
    );
  }

  getUserDisps(userId: number){
    return this._http.get<any>(
      `${AppConfig.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/userDisps/`+ userId
      );
  }

  getExcelData(dispId: number){
    return this._http.get<any>(
      `${AppConfig.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/excelData/`+ dispId
      );
  }

  addOrganisme(data){
    return this._http.post<any>(
      `${AppConfig.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/organisme`,
      data
    );
  }

  updateOrganisme(data){
    return this._http.put<any>(
      `${AppConfig.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/organisme`,
      data
    );
  }

  deleteOrganisme(data){
    const options = {
     headers: new HttpHeaders({
       'Content-Type': 'application/json',
     }),
     body: {
       "id_organisme":  data.id,
     },
   };
   return this._http.delete<any>(
     `${AppConfig.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/organisme`,
     options
   );
  }

  addDispositif(data){
    return this._http.post<any>(
      `${AppConfig.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/dispositif`,
      data
    );
  }

  updateDispositif(data){
    return this._http.put<any>(
      `${AppConfig.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/dispositif`,
      data
    );
  }

  deleteDisp(data){
    const options = {
     headers: new HttpHeaders({
       'Content-Type': 'application/json',
     }),
     body: {
       "id_dispositif":  data.id_dispositif,
     },
   };

   return this._http.delete<any>(
     `${AppConfig.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/dispositif`,
     options
   );
  }

  getCorDispositifRole(){
    return this._http.get<any>(
      `${AppConfig.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/corDispositifRole`
      );
  }

  psdrf_liste_update(file){
    let psdrf_liste:FormData = new FormData();
    psdrf_liste.append('file_upload', file, 'psdrfListe');
    return this._http.post<any>(
      `${AppConfig.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/psdrfListe`,
      psdrf_liste
    );
  }

}
