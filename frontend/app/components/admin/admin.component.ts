import {Component, Input, Output, EventEmitter, OnInit} from '@angular/core';
import { FormGroup, FormBuilder, Validators, FormControl } from '@angular/forms';
import { Router } from "@angular/router";
import { PsdrfDataService } from "../../services/route.service";
import { AppConfig } from '@geonature_config/app.config';
import { ToastrService } from 'ngx-toastr';
import { AuthService } from '@geonature/components/auth/auth.service';


@Component({
    selector: "rnf-psdrf-admin",
    templateUrl: "./admin.component.html",
    styleUrls: ["./admin.component.scss"],
  })
  export class AdminComponent implements OnInit{
    dispositifList : string[] = [];
    dispositifs = new FormControl();

    utilisateurList : string[] = [];
    utilisateurs = new FormControl();

    organismeList: string[]= [];

    form: FormGroup;
    dynamicFormGroup: FormGroup;

    userDispForm: FormGroup;
    dynamicUserDispFormGroup: FormGroup;

    organismeForm: FormGroup;
    dynamicOrganismeFormGroup: FormGroup;

    dispForm: FormGroup;
    dynamicDispFormGroup: FormGroup;

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
        private dataSrv: PsdrfDataService
    ) {
    }

    ngOnInit(){
        this.getUtilisateurList();
        this.getDispositifList();
        this.getOrganismeList();
        this.createForm();
        this.createUserDispForm();
        this.createDispForm();
        this.createOrganismeForm();
    }

    /**
   * Quit admin page
   */
    returnToPreviousPage(): void {
        this._router.navigate(["psdrf"]);
    }

    createForm() {
        this.form = this.fb.group({
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
        this.dynamicFormGroup = this.fb.group({});
      }

    createUserDispForm() {
      this.userDispForm = this.fbUserDisp.group({
        utilisateur: ['', Validators.required],
        dispositif: ['', Validators.required]
      });
      this.dynamicUserDispFormGroup = this.fbUserDisp.group({});
    }

    createDispForm() {
      this.dispForm = this.fbDisp.group({
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
            console.log(data)
            this.organismeList = data
        }
      );
    }

    save() {
        if (this.form.valid) {
          this.disableSubmit = true;
          this.form.value.password = "psdrf_mdp";
          this.form.value.password_confirmation = "psdrf_mdp";
          const finalForm = Object.assign({}, this.form.value);
          // concatenate two forms
          if (AppConfig.ACCOUNT_MANAGEMENT.ACCOUNT_FORM.length > 0) {
            finalForm['champs_addi'] = this.dynamicFormGroup.value;
          }
          this._authService
            .signupUser(finalForm)
            .subscribe(
              res => {
                this._toasterService.success("L'utilisateur a bien été ajouté", '');
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
        const finalForm = Object.assign({}, this.userDispForm.value);
        console.log(finalForm)
        this.dataSrv
          .addCorDispRole(finalForm)
          .subscribe(
            res => {          
              this._toasterService.success("Le dispositif "+ finalForm.dispositif +" a bien été ajouté à la liste des dispositifs modifiables par le rôle "+ finalForm.utilisateur, '');
            },
            // error callback
            error => {
              console.log(error)
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
        console.log(finalForm)
        this.dataSrv
          .addOrganisme(finalForm)
          .subscribe(
            res => {          
              this._toasterService.success("Le organisme "+ finalForm.newOrganisme +" a bien été ajouté", '');
            },
            // error callback
            error => {
              console.log(error)
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
        console.log(finalForm)
        this.dataSrv
          .addDispositif(finalForm)
          .subscribe(
            res => {          
              this._toasterService.success("Le dispositif "+ finalForm.newDispositif +" a bien été ajouté", '');
            },
            // error callback
            error => {
              console.log(error)
              this._toasterService.error(error.error.msg, '');
            }
          )
          .add(() => {
            this.disableSubmitDisp = false;
          });
      }
    }

  }