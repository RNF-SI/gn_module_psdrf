export class PsdrfError {
    message: string;
    table: string;
    column: string;
    row: number[];
    value: string;

    constructor(message: string, table: string, column: string, row: number[], value: string) {
        this.message = message;
        this.table = table;
        this.column = column; 
        this.row = row;
        this.value = value;
      }

    toPsdrfErrorCoordinates(rowIndex: number): PsdrfErrorCoordinates{
        return new PsdrfErrorCoordinates(this.table, this.column, this.row[rowIndex]);
    }

};

export class DuplicatedError {
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

    toPsdrfErrorCoordinates2(): PsdrfErrorCoordinates2{
        return new PsdrfErrorCoordinates2(this.table, this.column, this.row);
    }
}

// export class PsdrfError {
//     message: string;
//     table: string;
//     column: string;
//     isBlockingError: boolean;
//     row: number[] | undefined;
//     value: string | undefined;

//     constructor(isBlockingError: boolean, message: string, table: string, column: string, row?: number[], value?: string) {
//         this.isBlockingError = isBlockingError;
//         this.message = message;
//         this.table = table;
//         this.column = column; 
//         this.row = row;
//         this.value = value;
//       } 

//     toPsdrfErrorCoordinates(rowIndex: number): PsdrfErrorCoordinates{
//         return new PsdrfErrorCoordinates(this.table, this.column, this.row[rowIndex]);
//     }

//   };

export class PsdrfErrorCoordinates {
    table: string;
    column: string;
    row: number;

    constructor(table: string, column: string, row: number) {
        this.table = table;
        this.column = column;
        this.row = row;
      }
};

export class PsdrfErrorCoordinates2 {
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
        [key: number]: PsdrfErrorCoordinates2;
    }= {};

    constructor(lastSelectedIndex: number, errorCoordinates: PsdrfErrorCoordinates2){
        this.lastSelected = lastSelectedIndex;
        this.subStepHistory[lastSelectedIndex] = errorCoordinates;
    }

    setLastSelected(lastSelectedIndex: number): void{
        this.lastSelected = lastSelectedIndex;
    }

    updateSubStepHistory(subStepIndex: number, errorCoordinates: PsdrfErrorCoordinates2): void{
        this.subStepHistory[subStepIndex] = errorCoordinates;
    }


}