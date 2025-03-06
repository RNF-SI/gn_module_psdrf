import {Component, OnChanges, Input, Output, SimpleChanges, ChangeDetectorRef, EventEmitter } from '@angular/core';
import { MatTableDataSource } from '@angular/material/table';
import { MatDialog } from "@angular/material/dialog";
import { ConfirmationDialog } from "@geonature_common/others/modal-confirmation/confirmation.dialog";
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { ViewChild, AfterViewInit } from '@angular/core';




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
    @Input() tableName: string; 

    @Output() updatingRow = new EventEmitter<any>();
    @Output() deletingRow = new EventEmitter<any>();

    @ViewChild(MatPaginator) paginator: MatPaginator;
    @ViewChild(MatSort) sort: MatSort;

    public datasource=new MatTableDataSource<any>();

    constructor(
      private changeDetectorRefs: ChangeDetectorRef,
      public dialog: MatDialog

      ) { }


    ngOnChanges(changes: SimpleChanges){
      this.datasource.data = changes.data.currentValue || [];
    }

    ngAfterViewInit() {
      this.datasource.paginator = this.paginator;
      this.datasource.sort = this.sort;
    }

    applyFilter(filterValue: string) {
      this.datasource.filter = filterValue.trim().toLowerCase();
    }

    openUpdateForm(index, element){
      let returnObj = {"index": index, "element": element}
      this.updatingRow.next(returnObj);
    }

    deleteElement(index, element){
      const message = `Etes vous sûr de vouloir supprimer cet élément? `;
      const dialogRef = this.dialog.open(ConfirmationDialog, {
        width: "350px",
        position: { top: "5%" },
        data: { message: message },
      });
        
      dialogRef.afterClosed().subscribe((confirmed: boolean) => {
        if(confirmed){
          let deleteObj = {"index": index, "element": element}
          this.deletingRow.next(deleteObj);
        }      
      })

    }


}