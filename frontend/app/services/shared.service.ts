import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { PsdrfDataService } from "./route.service";
import { AuthService } from '@geonature/components/auth/auth.service';
import { of, Observable, forkJoin, Subject } from 'rxjs';


@Injectable()
export class SharedService {
    private isAdmin: boolean; 

    constructor(
        private dataSrv: PsdrfDataService,
        private _authService: AuthService, 
    ) { }
  
    setIsAdmin(): Observable<boolean>{
        let currentUser = this._authService.getCurrentUser()
        var subject = new Subject<boolean>();

        forkJoin(
            [this.dataSrv.getGroupeList(), this.dataSrv.getUserGroups(currentUser.id_role)]
        ).subscribe((res) =>{
            let groupList = res[0]
            let userGroups = res [1]
            let id_Admin_Group: number; 
            groupList.forEach((group) => {
              if(group.nom_utilisateur == "Grp_admin"){
                id_Admin_Group = group.id_utilisateur; 
              }
            })
            if (userGroups.includes(id_Admin_Group)){
                this.isAdmin = true; 
            } else {
                this.isAdmin = false;
            }
            subject.next(this.isAdmin)
        })
        return subject.asObservable();
    }

    getIsAdmin(): boolean{
        return this.isAdmin
    }

}
