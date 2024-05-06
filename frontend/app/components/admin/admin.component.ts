import {Component, Input, Output, EventEmitter, OnInit} from '@angular/core';
import { FormGroup, FormBuilder, Validators, FormControl } from '@angular/forms';
import { Router } from "@angular/router";
import { PsdrfDataService } from "../../services/route.service";
import { AppConfig } from '@geonature_config/app.config';
import { ToastrService } from 'ngx-toastr';
import { AuthService } from '@geonature/components/auth/auth.service';
import * as _ from "lodash";
import { MatDialog } from "@angular/material/dialog";
import { ConfirmationDialog } from "@geonature_common/others/modal-confirmation/confirmation.dialog";
import { Observable } from 'rxjs';
import { map, startWith } from 'rxjs/operators';


export interface UserDisp {
  nom_utilisateur: string;
  prenom_utilisateur: string;
  nom_dispositif: string;
}

export interface User {
  nom_utilisateur: string;
  prenom_utilisateur: string;
  email_utilisateur: string;
  identifiant_utilisateur: string;
  nom_organisme: string;
  remarque_utilisateur: string;
}

export interface Disp {
  id_dispositif: number;
  nom_dispositif: string;
  nom_organisme: string;
  alluvial: boolean;
}

export interface Orga {
  nom_organisme: string;
  adresse_organisme: string;
  cp_organisme: string;
  ville_organisme: string;
  telephone_organisme: string;
  email_organisme: string;
}


@Component({
    selector: "rnf-psdrf-admin",
    templateUrl: "./admin.component.html",
    styleUrls: ["./admin.component.scss"],
  })
  export class AdminComponent implements OnInit{

    displayedColumns : any= {
      "UserDisp": ["delete", "nom_utilisateur", "prenom_utilisateur", "nom_dispositif"],
      "User": ["nom_utilisateur", 'prenom_utilisateur', 'email_utilisateur', 'identifiant_utilisateur', 'nom_organisme', 'remarque_utilisateur'],
      "Disp": ["delete", "update", "id_dispositif", "nom_dispositif", 'nom_organisme', 'alluvial'],
      "Orga": ["delete", "update", "nom_organisme", "adresse_organisme", "cp_organisme", "ville_organisme", "telephone_organisme", "email_organisme"]
    }
    isUserDrawerShowing: boolean = false; 
    isUserDispDrawerShowing: boolean = false;
    isDispDrawerShowing: boolean = false;
    isOrganismeDrawerShowing: boolean = false;

    isUserDrawerMaj: boolean = false; 
    isUserDispDrawerMaj: boolean = false;
    isDispDrawerMaj: boolean = false;
    isOrganismeDrawerMaj: boolean = false;

    dispositifList : Disp[] = [];
    dispositifs = new FormControl();

    filteredUtilisateurs: Observable<User[]>;
    filteredDispositifs: Observable<Disp[]>;

    utilisateurList : User[] = [];
    utilisateurs = new FormControl();

    organismeList: Orga[]= [];

    userForm: FormGroup;
    dynamicUserFormGroup: FormGroup;


    userDispForm: FormGroup;
    userDispList: UserDisp[];

    organismeForm: FormGroup;
    dynamicOrganismeFormGroup: FormGroup;

    dispForm: FormGroup;
    dynamicDispFormGroup: FormGroup;

    majId: number; 

    private psdrfListeFile: any = null;
    private excelFileName: any;
    public isPsdrfListeCharging: any;
    private psdrfListUploading = false; 
    private isPSDRFListeLoaded= false;

    // Placette file variables
    private placetteFile: any = null;
    public isPlacetteCharging: boolean = false;
    private placetteUploading: boolean = false;
    private isPlacetteLoaded: boolean = false;


    public disableSubmit = false;
    public disableSubmitUserDisp = false;
    public disableSubmitOrganisme = false;
    public disableSubmitDisp = false;
    public formControlBuilded = false;
    public FORM_CONFIG = AppConfig.ACCOUNT_MANAGEMENT.ACCOUNT_FORM;

    constructor(
        private fb: FormBuilder,
        private fbUserDisp: FormBuilder,
        private fbDisp: FormBuilder,
        private fbOrganisme: FormBuilder,
        private _authService: AuthService,
        private _router: Router,
        private _toasterService: ToastrService,
        private dataSrv: PsdrfDataService,
        public dialog: MatDialog
    ) {
    }

    ngOnInit(){
        this.getUtilisateurList();
        this.getDispositifList();
        this.getOrganismeList();
        this.getUserDisps();

        this.createForm();
        this.createUserDispForm();
        this.createDispForm();
        this.createOrganismeForm();

        this.initFilter();

    }

    /**
   * Quit admin page
   */
    returnToPreviousPage(): void {
        this._router.navigate(["psdrf"]);
    }

    createForm() {
        this.userForm = this.fb.group({
          nom_role: ['', Validators.required],
          prenom_role: ['', Validators.required],
          identifiant: ['', Validators.required],
          email: [
            '',
            [Validators.pattern('^[+a-z0-9._-]+@[a-z0-9._-]{2,}.[a-z]{2,4}$'), Validators.required]
          ],
          remarques: ['', null],
          organisme: ['', null]
        });
        this.dynamicUserFormGroup = this.fb.group({});
      }

    createUserDispForm() {
      this.userDispForm = this.fbUserDisp.group({
        utilisateur: ['', Validators.required],
        dispositif: ['', Validators.required]
      });
    }

    createDispForm() {
      this.dispForm = this.fbDisp.group({
        idDispositif: ['', Validators.required],
        newDispositif: ['', Validators.required],
        dispOrganisme: ['', Validators.required],
        alluvial: [false, null]

      });
      this.dynamicDispFormGroup = this.fbDisp.group({});
    }

    createOrganismeForm(){
      this.organismeForm = this.fbOrganisme.group({
        newOrganisme: ['', Validators.required],
        adresseOrga: ['', null],
        cpOrga: ['', null],
        villeOrga: ['', null],
        telOrga: ['', null],
        mailOrga: ['', null]
      });
      this.dynamicOrganismeFormGroup = this.fbOrganisme.group({});
    }

    getDispositifList(): void{
        this.dataSrv
            .getDispositifList()
            .subscribe(
            (data: any) => {
                this.dispositifList = data;
            }
        );
    }

    getUtilisateurList(): void{
      this.dataSrv
          .getUtilisateurList()
          .subscribe(
          (data: any) => {
            this.utilisateurList = data
        }
      );
    }

    getOrganismeList(): void{
      this.dataSrv
          .getOrganismeList()
          .subscribe(
          (data: any) => {
            this.organismeList = data
        }
      );
    }
    
    getUserDisps(): void{
      this.dataSrv
          .getCorDispositifRole()
          .subscribe(
          (data: any) => {
            this.userDispList = data
        }
      );
    }

    initFilter() {
      this.filteredUtilisateurs = this.userDispForm.get('utilisateur').valueChanges
        .pipe(
          startWith(''),
          map(value => typeof value === 'string' ? this.filter('utilisateur', value) : this.filter('utilisateur', ''))
        );
    
      this.filteredDispositifs = this.userDispForm.get('dispositif').valueChanges
        .pipe(
          startWith(''),
          map(value => typeof value === 'string' ? this.filter('dispositif', value) : this.filter('dispositif', ''))
        );
    }

    filter(type: string, value: string): any[] {
      const filterValue = value.toLowerCase();
      return type === 'utilisateur' ?
        this.utilisateurList.filter(option => (option.nom_utilisateur + ' ' + option.prenom_utilisateur).toLowerCase().includes(filterValue)) :
        this.dispositifList.filter(option => option.nom_dispositif.toLowerCase().includes(filterValue));
    }
  
    displayFn(userOrDisp: any): string {
      return userOrDisp ? (userOrDisp.nom_utilisateur ? `${userOrDisp.nom_utilisateur} ${userOrDisp.prenom_utilisateur}` : userOrDisp.nom_dispositif) : '';
    }
    

    save() {
      if (this.userForm.valid) {
        this.disableSubmit = true;
        this.userForm.value.password = "psdrf_mdp";
        this.userForm.value.password_confirmation = "psdrf_mdp";
        const finalForm = Object.assign({}, this.userForm.value);
        console.log(finalForm)
        // concatenate two forms
        if (AppConfig.ACCOUNT_MANAGEMENT.ACCOUNT_FORM.length > 0) {
          finalForm['champs_addi'] = this.dynamicUserFormGroup.value;
        }
        this._authService
          .signupUser(finalForm)
          .subscribe(
            res => {
              this._toasterService.success("L'utilisateur a bien été ajouté", '');
              this.getUtilisateurList();
            },
            // error callback
            error => {
              this._toasterService.error(error.error.msg, '');
            }
          )
          .add(() => {
            this.disableSubmit = false;
          });
      }
    }

    update() {
      if (this.userForm.valid) {
        this.disableSubmit = true;
        this.userForm.value.password = "psdrf_mdp";
        this.userForm.value.password_confirmation = "psdrf_mdp";
        const finalForm = Object.assign({}, this.userForm.value);
        // concatenate two forms
        if (AppConfig.ACCOUNT_MANAGEMENT.ACCOUNT_FORM.length > 0) {
          finalForm['champs_addi'] = this.dynamicUserFormGroup.value;
        }
        this._authService
          .signupUser(finalForm)
          .subscribe(
            res => {
              this._toasterService.success("L'utilisateur a bien été ajouté", '');
              this.getUtilisateurList();
            },
            // error callback
            error => {
              this._toasterService.error(error.error.msg, '');
            }
          )
          .add(() => {
            this.disableSubmit = false;
          });
      }
    }

    addRoleDisp() {
      if (this.userDispForm.valid) {
        this.disableSubmitUserDisp = true;
        // Extracting IDs or necessary properties
        const finalForm = {
          utilisateur: this.userDispForm.value.utilisateur.id_utilisateur,  // Adjust 'id' based on actual property
          dispositif: this.userDispForm.value.dispositif.id_dispositif    // Adjust 'id' based on actual property
        };
    
        this.dataSrv.addCorDispRole(finalForm)
          .subscribe(
            res => {
              this._toasterService.success("Le dispositif " + finalForm.dispositif + " a bien été ajouté à la liste des dispositifs modifiables par le rôle " + finalForm.utilisateur, '');
              this.getUserDisps();
            },
            error => {
              this._toasterService.error(error.error.msg, '');
            }
          )
          .add(() => {
            this.disableSubmitUserDisp = false;
          });
      }
    }
    

    updateRoleDisp() {
      if (this.userDispForm.valid) {
        this.disableSubmitUserDisp = true;
        const finalForm = Object.assign({}, this.userDispForm.value);
        this.dataSrv
          .updateCorDispRole(finalForm)
          .subscribe(
            res => {          
              this._toasterService.success("Le lien dispositif-rôle a été modifié", '');
              this.getUserDisps();
            },
            // error callback
            error => {
              this._toasterService.error(error.error.msg, '');
            }
          )
          .add(() => {
            this.disableSubmitUserDisp = false;
          });
      }
    }

    addOrganisme() {
      if (this.organismeForm.valid) {
        this.disableSubmitOrganisme = true;
        const finalForm = Object.assign({}, this.organismeForm.value);
        this.dataSrv
          .addOrganisme(finalForm)
          .subscribe(
            res => {          
              this._toasterService.success("L'organisme "+ finalForm.newOrganisme +" a bien été ajouté", '');
              this.getOrganismeList();
            },
            // error callback
            error => {
              this._toasterService.error(error.error.msg, '');
            }
          )
          .add(() => {
            this.disableSubmitOrganisme = false;
          });
      }
    }

    updateOrganisme() {
      if (this.organismeForm.valid) {
        this.disableSubmitOrganisme = true;
        const finalForm = Object.assign({}, this.organismeForm.value);
        console.log(finalForm)
        finalForm.id_organisme = this.majId
        this.dataSrv
          .updateOrganisme(finalForm)
          .subscribe(
            res => {          
              this._toasterService.success("L'organisme "+ finalForm.newOrganisme +" a bien été modifié", '');
              this.getOrganismeList();
            },
            // error callback
            error => {
              this._toasterService.error(error.error.msg, '');
            }
          )
          .add(() => {
            this.disableSubmitOrganisme = false;
          });
      }
    }
    
    addDisp() {
      if (this.dispForm.valid) {
        this.disableSubmitDisp = true;
        const finalForm = Object.assign({}, this.dispForm.value);

        if(finalForm["alluvial"] == ""){
          finalForm["alluvial"]= false;
        }

        this.dataSrv
        .addDispositif(finalForm)
        .subscribe(
          res => {          
            this._toasterService.success("Le dispositif "+ finalForm.newDispositif +" a bien été ajouté", '');
            this.getDispositifList();
            },
            // error callback
            error => {
              this._toasterService.error(error.error.msg, '');
            }
          )
          .add(() => {
            this.disableSubmitDisp = false;
          });
      }
    }

    updateDisp() {
      if (this.dispForm.valid) {
        this.disableSubmitDisp = true;
        const finalForm = Object.assign({}, this.dispForm.value);
        finalForm.id_dispositif = this.majId

        this.dataSrv
        .updateDispositif(finalForm)
        .subscribe(
          res => {          
            this._toasterService.success("Le dispositif "+ finalForm.newDispositif +" a bien été modifié", '');
            this.getDispositifList();
            },
            // error callback
            error => {
              this._toasterService.error(error.error.msg, '');
            }
          )
          .add(() => {
            this.disableSubmitDisp = false;
          });
      }
    }


    openUpdateForm(updatingInformation: any, drawer: string){
      console.log(updatingInformation)
      let element = updatingInformation.element;
      // if(drawer=='userDrawer'){
      //   this.isUserDrawerShowing = true;
      //   this.isUserDrawerMaj = true;
      //   this.userForm.setValue({
      //     nom_role: element.nom_utilisateur,
      //     prenom_role: element.prenom_utilisateur,
      //     identifiant: element.identifiant_utilisateur,
      //     email: element.email_utilisateur,
      //     remarques: element.remarques_utilisateur,
      //     organisme: element.id_organisme
      //   });
      // } else if (drawer=='userDispDrawer'){
      //   this.isUserDispDrawerMaj = true;
      //   this.isUserDispDrawerShowing = true;
      //   this.userDispForm.setValue({
      //     utilisateur: element.id_utilisateur,
      //     dispositif: element.id_dispositif
      //   });
      // } else
      if (drawer=='dispDrawer'){
        console.log(element)
        this.majId = element.id_dispositif;
        this.isDispDrawerMaj = true;
        this.isDispDrawerShowing = true;
        this.dispForm.setValue({
          idDispositif: element.id_dispositif,
          newDispositif: element.nom_dispositif,
          dispOrganisme: element.id_organisme,
          alluvial: element.alluvial
        });
      } else if (drawer=='organismeDrawer'){
        console.log(element)
        this.isOrganismeDrawerShowing = true;
        this.isOrganismeDrawerMaj = true;
        this.majId = element.id;
        this.organismeForm.setValue({
          newOrganisme: element.nom_organisme,
          adresseOrga: element.adresse_organisme,
          cpOrga: element.cp_organisme,
          villeOrga: element.ville_organisme,
          telOrga: element.telephone_organisme,
          mailOrga: element.email_organisme
        });
      }
    }

    openCreationForm(drawer: string){
      if(drawer=='userDrawer'){
        this.isUserDrawerShowing = true;
        this.isUserDrawerMaj = false;
        this.userForm.setValue({
          nom_role: "",
          prenom_role: "",
          identifiant: "",
          email: "",
          remarques: "",
          organisme: ""
        });
      } else if (drawer=='userDispDrawer'){
        this.isUserDispDrawerShowing = true;
        this.isUserDispDrawerMaj = false;
        this.userDispForm.setValue({
          utilisateur: "",
          dispositif: ""
        });
      } else if (drawer=='dispDrawer'){
        this.isDispDrawerShowing = true;
        this.isDispDrawerMaj = false;
        this.dispForm.setValue({
          idDispositif: "",
          newDispositif: "",
          dispOrganisme: "",
          alluvial: ""
        });
      } else if (drawer=='organismeDrawer'){
        this.isOrganismeDrawerShowing = true;
        this.isOrganismeDrawerMaj = false;
        this.organismeForm.setValue({
          newOrganisme: "",
          adresseOrga: "",
          cpOrga: "",
          villeOrga: "",
          telOrga: "",
          mailOrga: ""
        });
      }
    }

    deleteRow(deletingInformation: any, drawer: string){
      let element = deletingInformation.element
      console.log(element)
      switch (drawer){
        case "userDisp":
          this.dataSrv
            .deleteCorDispRole(element)
            .subscribe(
            (data: any) => {
              this._toasterService.success("L'utilisateur"+ element.nom_utilisateur + " "+  element.prenom_utilisateur+"  n'a plus les droits sur le dispositif "+ element.nom_dispositif, '');
              this.getUserDisps();
            }
          );
          break;
        case "disp":
          this.dataSrv
            .deleteDisp(element)
            .subscribe(
            (data: any) => {
              this._toasterService.success("Le dispositif "+ element.nom_dispositif+" a bien été supprimé.", '');
              this.getDispositifList();
            }
          );
          break;
        case "organisme":
          this.dataSrv
            .deleteOrganisme(element)
            .subscribe(
            (data: any) => {
              this._toasterService.success("L'Organisme "+ element.nom_organisme+" a bien été supprimé.", '');
              this.getOrganismeList();
            }
          );
          break;
      }
    }

    toggleUserDrawer() {
      this.isUserDrawerShowing = !this.isUserDrawerShowing;
      if(this.isUserDrawerShowing){
        this.openCreationForm('userDrawer');
      }
    }

    toggleUserDispDrawer() {
      this.isUserDispDrawerShowing = !this.isUserDispDrawerShowing;
      if(this.isUserDispDrawerShowing){
        this.openCreationForm('userDispDrawer');
      }
    }

    toggleDispDrawer() {
      this.isDispDrawerShowing = !this.isDispDrawerShowing;
      if(this.isDispDrawerShowing){
        this.openCreationForm('dispDrawer');
      }
    }

    toggleOrganismeDrawer() {
      this.isOrganismeDrawerShowing = !this.isOrganismeDrawerShowing;
      if(this.isOrganismeDrawerShowing){
        this.openCreationForm('organismeDrawer');
      }
    }

    compareCategoryObjects(object1: any, object2: any) {
      return object1 && object2 && object1 == object2;
    }

  /**
   * Triggered function on D&D event
   * @param event Drag and Drop event
   */
   onPSDRFListeDropped(event: DragEvent): void {
    let af = [
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      "application/vnd.ms-excel",
    ];
    let files = event.dataTransfer.files;
    if (files.length !== 1) throw new Error("Cannot use multiple files");
    const file = files[0];
    if (!_.includes(af, file.type)) {
      alert("Only EXCEL Docs Allowed!");
    } else {
      this.psdrfListeFile = file;
      const target: DataTransfer = event.dataTransfer;
      this.loadPSDRFListe(target);
    }
  }

  /**
   *  Triggered function on file selection (a file is chosen)
   * @param event Selection File Event
   */
  onPSDRFListeSelect(event): void {
    const target: DataTransfer = <DataTransfer>event.target;
    if (target.files.length !== 1) throw new Error("Cannot use multiple files");
    this.psdrfListeFile = target.files[0];
    this.loadPSDRFListe(target);
  }

  loadPSDRFListe(psdrfListe: DataTransfer): void {
    const reader: FileReader = new FileReader();
    this.excelFileName = psdrfListe.files[0].name;
    
    let numDisp = this.excelFileName.split("-")[0];
    this.isPsdrfListeCharging = true;


      reader.onload = (e: any) => {
        this.isPSDRFListeLoaded = true;
      };

      reader.onerror = (e: any) => {
        this._toasterService.error("Un problème a été rencontré lors du chargement du fichier Excel.", "Chargement des données du fichier Excel", {
          closeButton: true,
          disableTimeOut: true,
        });
      };

      reader.onloadend = (e) => {
      };
  }

   /**
   * Delete the loaded Excel file
   */
    deleteFile(): void {

      const message = `Etes vous sûr de vouloir supprimer vos modifications? `;
      const dialogRef = this.dialog.open(ConfirmationDialog, {
        width: "350px",
        position: { top: "5%" },
        data: { message: message },
      });
  
      
      dialogRef.afterClosed().subscribe((confirmed: boolean) => {
        if(confirmed){
          this.isPSDRFListeLoaded = false;
          this.psdrfListeFile = null;
          this.isPsdrfListeCharging = false;
        }      
      })
    }

    psdrfListeUpdate(){
      this.psdrfListUploading = true;   
      this.dataSrv
        .psdrf_liste_update(
          this.psdrfListeFile
        )
        .subscribe(
          integrationObj => {
            this.psdrfListUploading = false;   
            if(integrationObj.success){
              this._toasterService.success("PSDRF liste a bien été actualisée", "Mise à jour de PSDRF liste", {
                closeButton: true,
                disableTimeOut: true,
              });
            } else {
              this._toasterService.error("Une erreur s'est produite lors de l'actualisation de psdrf liste.", "Mise à jour de PSDRF liste", {
                closeButton: true,
                disableTimeOut: true,
              });
            }

          },
          error => {
            this._toasterService.error(error.message, "Mise à jour de PSDRF liste", {
              closeButton: true,
              disableTimeOut: true,
            });
            this.psdrfListUploading = false;
            this.isPSDRFListeLoaded = false;
            
          }
        );
    }

    // Placette File Part
    // Add methods for handling Placette file events
onPlacetteDropped(event: DragEvent): void {
  let allowedFormats = [
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel",
  ];
  let files = event.dataTransfer.files;
  if (files.length !== 1) throw new Error("Cannot use multiple files");
  const file = files[0];
  if (!_.includes(allowedFormats, file.type)) {
    alert("Only EXCEL Docs Allowed!");
  } else {
    this.placetteFile = file;
    this.isPlacetteCharging = true;
    // You might need to implement loadPlacette method similar to loadPSDRFListe
  }
}

onPlacetteSelect(event): void {
  const target: DataTransfer = <DataTransfer>event.target;
  if (target.files.length !== 1) throw new Error("Cannot use multiple files");
  this.placetteFile = target.files[0];
  this.isPlacetteCharging = true;
  // You might need to implement loadPlacette method similar to loadPSDRFListe
}

deletePlacetteFile(): void {
  // Implement the logic for deleting the placette file
  this.isPlacetteLoaded = false;
  this.placetteFile = null;
  this.isPlacetteCharging = false;
}

placetteUpdate(): void {
  this.placetteUploading = true;
  this.dataSrv.disp_placette_liste_update(this.placetteFile) // Change the method name as per your service
    .subscribe(
      response => {
        this.placetteUploading = false;
        if (response.success) {

          this._toasterService.success(response.message, "Mise à jour de la liste de placettes", {
            closeButton: true,
            disableTimeOut: true,
          });

        } else {
          this._toasterService.error("Error: " + response.message, "Mise à jour de la liste de placettes", {
            closeButton: true,
            disableTimeOut: true,
          });
        }
      },
      error => {
        this._toasterService.error(error.message, "Mise à jour de la liste de placettes", {
          closeButton: true,
          disableTimeOut: true,
        });
        // Handle HTTP errors
        this.placetteUploading = false;
        this.isPlacetteLoaded = false;
      }
    );
}


}
