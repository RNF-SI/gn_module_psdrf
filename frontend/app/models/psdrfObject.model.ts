export class PsdrfError {
    message: string;
    table: string|null;
    column: string[]|null;
    row: number[]|null;
    value: any|null;

    constructor(message: string, table: string|null, column: string[]|null, row: number[]|null, value: any) {
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
    table: string|null;
    column: string[]|null;
    row: number[]|null;

    constructor(table: string|null, column: string[]|null, row: number[]|null) {
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
