import { Component, OnInit } from "@angular/core";
import { PsdrfDataService } from "../services/route.service";

@Component({
  selector: "rnf-dendro-download",
  templateUrl: "dendro-download.component.html",
  styleUrls: ["dendro-download.component.scss"]
})
export class DendroDownloadComponent implements OnInit {
  constructor(
    private dataSrv: PsdrfDataService, 

  ) {}

  ngOnInit() {}

  downloadDendro() {
    this.dataSrv.getDendroApk().subscribe(
      blob => {
        const url = window.URL.createObjectURL(blob);
        const anchor = document.createElement('a');
        anchor.download = 'Dendro3.apk';
        anchor.href = url;
        anchor.click();
        window.URL.revokeObjectURL(url);  // Clean up the URL object
      },
      error => {
        console.error('Erreur de Téléchargement:', error);
      }
    );
  }
}