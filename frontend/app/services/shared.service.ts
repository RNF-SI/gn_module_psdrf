import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { PsdrfDataService } from "./route.service";
import { AuthService } from '@geonature/components/auth/auth.service';
import { of, Observable, forkJoin, Subject } from 'rxjs';


@Injectable()
export class SharedService {
    private isPsdrfAdmin: boolean; 

    constructor(
        private dataSrv: PsdrfDataService,
        private _authService: AuthService, 
    ) { }
  
    setPsdrfAdmin(): Observable<boolean>{
        let currentUser = this._authService.getCurrentUser()
        var subject = new Subject<boolean>();

        forkJoin(
            [this.dataSrv.getGroupeList(), this.dataSrv.getUserGroups(currentUser.id_role)]
        ).subscribe((res) =>{
            let groupList = res[0]
            let userGroups = res [1]
            let id_PSDRF_Group: number; 
            groupList.forEach((group) => {
              if(group.nom_utilisateur == "PSDRF"){
                id_PSDRF_Group = group.id_utilisateur; 
              }
            })
            if (userGroups.includes(id_PSDRF_Group)){
                this.isPsdrfAdmin = true; 
            } else {
                this.isPsdrfAdmin = false;
            }
            subject.next(this.isPsdrfAdmin)
        })
        return subject.asObservable();
    }

    getPsdrfAdmin(): boolean{
        return this.isPsdrfAdmin
    }

}