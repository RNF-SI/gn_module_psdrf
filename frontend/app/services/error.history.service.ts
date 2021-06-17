import { Injectable } from '@angular/core';
import {PsdrfErrorCoordinates, MainStepHistory} from '../models/psdrfObject.model';


@Injectable()
export class ErrorHistoryService{
    private historyList:{[key: number]: MainStepHistory} = {}; //historique

     /**
   * Save a substep in the history array when this one has been clicked
   * @param psdrfErrorCoor PsdrfErrorCoordinates of the entire substep
   * @param mainStepIndex index of the mainstep
   * @param subStepIndex index of the substep
   */
    rememberSubStep(errorCoor: PsdrfErrorCoordinates, mainStepIndex: number, subStepIndex: number): void{
        if(this.historyList[mainStepIndex]){
            this.historyList[mainStepIndex].setLastSelected(subStepIndex);
            this.historyList[mainStepIndex].updateSubStepHistory(subStepIndex, errorCoor);
        } else {
            this.historyList[mainStepIndex] = new MainStepHistory(subStepIndex, errorCoor);
        }
    }

    /**
   * Retourne les dernières coordonnées cliquée à partir du mainStepIndex
    Si c'est un bouton mainStep qui a été cliqué, alors le fonctionnement est simple: on récupère
    les coordonnées du lastSelectedIndex sans se poser de questions
    Si c'est un bouton subStep qui a été cliqué, alors la fonction rememberSubStep a été appelée
    juste avant. Dedans, on a changé le lastSelectedIndex pour l'index du step qu'on vient de cliquer. 
    Donc la property lastSelected contient la bonne valeur.
   * @param mainStepIndex index of the mainstep
   */
    getLastSelectedCoordinates(mainStepIndex: number): PsdrfErrorCoordinates{
        let mainStepHistory = this.historyList[mainStepIndex];
        return mainStepHistory.subStepHistory[mainStepHistory.lastSelected];
    }

 
    /**
   * Return True if there is a value for a mainStep in historyList
   * @param mainStepIndex index of the mainstep
   */
    isMainStepHasAlreadyBeenClicked(mainStepIndex: number): boolean{
        if(this.historyList[mainStepIndex]){
            return true; 
        } else {
            return false; 
        }
    }

    /**
   * Return True if there is a value for a subStep in historyList
   * @param mainStepIndex index of the mainstep
   */
    isSubStepHasAlreadyBeenClicked(mainStepIndex: number, subStepIndex: number): boolean{
        if(this.historyList[mainStepIndex].subStepHistory[subStepIndex]){
            return true; 
        } else {
            return false; 
        }
    }

    /**
   * Empty historyList
   */
    reInitialize(): void{
        this.historyList = {};
    }
}