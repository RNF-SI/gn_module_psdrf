import {Component, OnChanges, Input, SimpleChanges, ChangeDetectorRef } from '@angular/core';
import { MatTableDataSource } from '@angular/material/table';




/**
 * @title Basic use of `<table mat-table>`
 */
@Component({
  selector: 'admin-table',
  styleUrls: ['admin-table.component.scss'],
  templateUrl: 'admin-table.component.html',
})
export class AdminTableComponent implements OnChanges {
    @Input() displayedColumns: string[];
    @Input() data= []; 
    public datasource=new MatTableDataSource<any>();

    constructor(private changeDetectorRefs: ChangeDetectorRef) { }


    ngOnChanges(changes: SimpleChanges){
        this.data = changes.data.currentValue;
        this.datasource = new MatTableDataSource<any>(this.data);
        this.changeDetectorRefs.detectChanges();
    }


}