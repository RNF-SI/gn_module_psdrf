import { Injectable } from "@angular/core";
import { Observable, throwError, interval } from 'rxjs';
import { HttpClient, HttpHeaders, HttpParams } from "@angular/common/http";
import { HttpResponse } from '@angular/common/http';
import { ConfigService } from '@geonature/services/config.service';
import { ModuleConfig } from "../module.config";
import { map, switchMap, filter, take, catchError } from 'rxjs/operators';

interface TaskResponse {
  task_id: string;
}

@Injectable()
export class PsdrfDataService {
  constructor(
    private _http: HttpClient,
    public config: ConfigService,

  ) {}

  psdrf_data_verification(data) {
    const httpOptions = {
      headers: { 'Content-Type': 'application/json' },
    };
    return this._http.post<any>(
      `${this.config.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/validation`,
      data,
      httpOptions
    );
  }

  psdrf_data_verification_with_shape(excelAndShapeData) {
    return this._http.post<any>(
      `${this.config.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/shapeValidation`,
      excelAndShapeData
    );
  }

  psdrfIntegrationToDatabase(data){
    return this._http.post<any>(
      `${this.config.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/integration`,
      data
    ); 
  }

  psdrf_data_analysis(id: number, isCarnetToDownload: boolean, isPlanDesArbresToDownload: boolean, parameters: {name: string, text: string, value: any}[] ) {
    const headers = new HttpHeaders({ 'Content-Type': 'application/json', responseType : 'blob'});
  
    let url = `${this.config.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/analysis/`+ id
    let params = new HttpParams().set("isCarnetToDownload",isCarnetToDownload.toString()).set("isPlanDesArbresToDownload",isPlanDesArbresToDownload.toString())
    //Ajouter les paramètres relatifs à la génération des documents
    parameters.forEach(param => {
      params= params.append(param.name, param.value.toString());
    })
  
    return this._http.get(
      url, 
      { observe: "response", headers : headers, params: params }
      )
      .pipe(
        map((res: HttpResponse<TaskResponse>) => {
          return res.body.task_id;
        })
      )
      .catch((err) => {
        return Observable.throw(err);
      });
  }
  
  get_task_status(taskId: string) {
    const url = `${this.config.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/analysis/status/` + taskId;
    return this._http.get(url).pipe(
      map((response: any) => {
        // Ensure response is properly formatted or extracted
        return response;
      }),
      catchError((error) => {
        // Handle error
        return throwError(error);
      })
    );
  }

  get_task_result(taskId: string, dispId: number) {
    const url = `${this.config.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/analysis/result/` + taskId;
    return this._http.get(url, { responseType: 'blob' })  // set responseType to 'blob' to handle files
      .pipe(
        map((blob: any) => {
          return {
            zip: blob,  // the file content
            filename: 'documents_dispositif_' +dispId+ '.zip'  // this should be dynamically set if the server provides the filename
          };
        }),
        catchError((err) => {
          return throwError(err);
        })
      );
  }

  getDispositifList(){
    return this._http.get<any>(
      `${this.config.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/dispositifsList`
    );
  }

  getUtilisateurAndGroupsList(){
    return this._http.get<any>(
      `${this.config.API_ENDPOINT}/users/roles`

      );
  }

  getUtilisateurList(){
    return this._http.get<any>(
      `${this.config.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/users`
      );
  }

  getGroupeList(){
    return this._http.get<any>(
      `${this.config.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/groups`
      );
  }

  getOrganismeList(){
    return this._http.get<any>(
      `${this.config.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/listOrganism`

      );
  }

  getUserGroups(userId: number){
    return this._http.get<any>(
      `${this.config.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/groupList/`+ userId

      );
  }

  addCorDispRole(data){
    return this._http.post<any>(
      `${this.config.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/corDispositifRole`,
      data
    );
  }

  updateCorDispRole(data){
    return this._http.put<any>(
      `${this.config.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/corDispositifRole`,
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
      `${this.config.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/corDispositifRole`,
      options
    );
  }

  getUserDisps(userId: number){
    return this._http.get<any>(
      `${this.config.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/userDisps/`+ userId
      );
  }

  getExcelProdData(dispId: number): Observable<any> {
    return this._http.get<any>(
      `${this.config.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/excelProdData/${dispId}`
    );
  }

  getExcelStagingData(dispId: number): Observable<any> {
    return this._http.get<any>(
      `${this.config.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/excelStagingData/${dispId}`
    );
  }

  addOrganisme(data){
    return this._http.post<any>(
      `${this.config.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/organisme`,
      data
    );
  }

  updateOrganisme(data){
    return this._http.put<any>(
      `${this.config.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/organisme`,
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
     `${this.config.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/organisme`,
     options
   );
  }

  addDispositif(data){
    return this._http.post<any>(
      `${this.config.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/dispositif`,
      data
    );
  }

  updateDispositif(data){
    return this._http.put<any>(
      `${this.config.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/dispositif`,
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
     `${this.config.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/dispositif`,
     options
   );
  }

  getCorDispositifRole(){
    return this._http.get<any>(
      `${this.config.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/corDispositifRole`
      );
  }

  psdrf_liste_update(formData: FormData) {
    return this._http.post<any>(
        `${this.config.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/psdrfListe`,
        formData
    );
  }


  disp_placette_liste_update(file){
    let disp_placette_liste:FormData = new FormData();
    disp_placette_liste.append('file_upload', file, 'disp_placette_liste');
    return this._http.post<any>(
      `${this.config.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/disp_placette_liste`,
      disp_placette_liste
    );
  }

  getDendroApk(): Observable<Blob> {
    const url = `${this.config.API_ENDPOINT}/${ModuleConfig.MODULE_URL}/dendro_apk`;
    return this._http.get(url, {
      responseType: 'blob'  // Important: Handle response as a blob
    });
  }


}
