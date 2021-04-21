import { Injectable } from '@angular/core';
import {PsdrfErrorCoordinates, MainStepHistory} from '../models/psdrfObject.model';


@Injectable()
export class ErrorHistoryService{
    private historyList:{[key: number]: MainStepHistory} = {}; //historique

    /*
        Sauvegarde l'index d'une ligne du tableau dans l'historique
    */
    rememberIndex(psdrfErrorCoor: PsdrfErrorCoordinates, rowIndex: number, mainStepIndex: number, subStepIndex: number): void{
        if(this.historyList[mainStepIndex]){
            this.historyList[mainStepIndex].setLastSelected(subStepIndex);
            this.historyList[mainStepIndex].updateSubStepHistory(subStepIndex, psdrfErrorCoor);
        } else {
            this.historyList[mainStepIndex] = new MainStepHistory(subStepIndex, psdrfErrorCoor);
        }
    }

    /*
        Sauvegarde un SubStep dans l'historique
    */
    rememberSubStep(subStepIndex: number, errorCoor: PsdrfErrorCoordinates, mainStepIndex: number): void{
        if(this.historyList[mainStepIndex]){
            this.historyList[mainStepIndex].setLastSelected(subStepIndex);
            //On initialise le subStepHistory du subStep en question si nécessaire
            //MAIS on ne le remplace pas si celui-ci existe déjà
            //Explications: Si il existe déjà, cela peut signifier que la fonction rememberIndex a déjà été appelée
            //On préfère donc garder le dernier index sur lequel on était
            if(this.historyList[mainStepIndex].subStepHistory[subStepIndex] == undefined){
                this.historyList[mainStepIndex].updateSubStepHistory(subStepIndex, errorCoor);
            } 
        } else {
            this.historyList[mainStepIndex] = new MainStepHistory(subStepIndex, errorCoor);
        }
    }

    /*
        Retourne les dernières coordonnées cliquée à partir du mainStepIndex
        Si c'est un bouton mainStep qui a été cliqué, alors le fonctionnement est simple: on récupère
        les coordonnées du lastSelectedIndex sans se poser de questions
        Si c'est un bouton subStep qui a été cliqué, alors la fonction rememberSubStep a été appelée
        juste avant. Dedans, on a changé le lastSelectedIndex pour l'index du step qu'on vient de cliquer. 
        Donc la property lastSelected contient la bonne valeur.
    */
    getLastSelectedCoordinates(mainStepIndex: number): PsdrfErrorCoordinates{
        let mainStepHistory = this.historyList[mainStepIndex];
        return mainStepHistory.subStepHistory[mainStepHistory.lastSelected];
    }

    /*
        Teste si il y a une valeur pour un mainStep donné dans historyList
    */
    isMainStepHasAlreadyBeenClicked(mainStepIndex: number): boolean{
        if(this.historyList[mainStepIndex]){
            return true; 
        } else {
            return false; 
        }
    }

    /*
        Teste si il y a une valeur pour un subStep donné dans historyList
    */
    isSubStepHasAlreadyBeenClicked(mainStepIndex: number, subStepIndex: number): boolean{
        if(this.historyList[mainStepIndex].subStepHistory[subStepIndex]){
            return true; 
        } else {
            return false; 
        }
    }

    reInitialize(): void{
        this.historyList = {};
    }
}