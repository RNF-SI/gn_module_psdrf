export class PsdrfError {
    message: string;
    table: string;
    column: string[];
    row: number[];
    value: any;

    constructor(message: string, table: string, column: string[], row: number[], value: any) {
        this.message = message;
        this.table = table;
        this.column = column; 
        this.row = row;
        this.value = value;
    } 

    toPsdrfErrorCoordinates(): PsdrfErrorCoordinates{
        return new PsdrfErrorCoordinates(this.table, this.column, this.row);
    }
}

export class PsdrfErrorCoordinates {
    table: string;
    column: string[];
    row: number[];

    constructor(table: string, column: string[], row: number[]) {
        this.table = table;
        this.column = column;
        this.row = row;
      }
};

export class MainStepHistory{
    lastSelected: number;
    subStepHistory:{
        [key: number]: PsdrfErrorCoordinates;
    }= {};

    constructor(lastSelectedIndex: number, errorCoordinates: PsdrfErrorCoordinates){
        this.lastSelected = lastSelectedIndex;
        this.subStepHistory[lastSelectedIndex] = errorCoordinates;
    }

    setLastSelected(lastSelectedIndex: number): void{
        this.lastSelected = lastSelectedIndex;
    }

    updateSubStepHistory(subStepIndex: number, errorCoordinates: PsdrfErrorCoordinates): void{
        this.subStepHistory[subStepIndex] = errorCoordinates;
    }


}