import { Component, OnInit } from "@angular/core";
import { PsdrfDataService } from "../services/route.service";

@Component({
  selector: "rnf-dendro-download",
  templateUrl: "dendro-download.component.html",
  styleUrls: ["dendro-download.component.scss"]
})
export class DendroDownloadComponent implements OnInit {
  loading = false;  // Loading state

  constructor(private dataSrv: PsdrfDataService) {}

  ngOnInit() {}

  downloadDendro() {
    this.loading = true;  // Set loading to true when download starts
    this.dataSrv.getDendroApk().subscribe(
      blob => {
        this.saveFile(blob, 'Dendro3.apk');
        this.loading = false;  // Set loading to false when download completes
      },
      error => {
        console.error('Erreur de Téléchargement:', error);
        this.loading = false;  // Set loading to false if an error occurs
      }
    );
  }

  private saveFile(blob: Blob, filename: string) {
    const url = window.URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.style.display = 'none';
    document.body.appendChild(anchor);
    anchor.href = url;
    anchor.download = filename;
    anchor.click();
    window.URL.revokeObjectURL(url);  // Clean up the URL object
    document.body.removeChild(anchor);
  }
}
