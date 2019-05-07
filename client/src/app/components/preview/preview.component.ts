import {Component, OnInit} from '@angular/core';
import {DataService} from '../../services/data.service';
import {EditorComponent} from '../editor/editor.component';
import {MatDialog} from '@angular/material';

@Component({
  selector: 'app-preview',
  templateUrl: './preview.component.html',
  styleUrls: ['./preview.component.css']
})
export class PreviewComponent implements OnInit {

  templateImgURL = null;
  previewImgURL = null;

  sourceURL = null;

  constructor(public dataService: DataService, public dialog: MatDialog) {
  }

  ngOnInit() {
    this.dataService.template.$options.subscribe((data) => {
      console.log('template changed');
      const url = data.url;
      this.templateImgURL = url;
      this.sourceURL = url;
    });
    this.dataService.design.$options.subscribe((data) => {
      if (data) {
        this.openDialog(data);
      }
    });
    this.dataService.preview.$options.subscribe((data) => {
      if (data == null) {
        this.previewImgURL = null;
        return;
      }
      this.previewImgURL = data['preview']['url'];
      this.updatePreviewSource();
    });
    this.dataService.preview.$reset.subscribe(() => {
      this.previewImgURL = null;
      this.updatePreviewSource();
    });
    this.dataService.colored.$options.subscribe(() => {
      this.updatePreviewSource();
    });
  }

  updatePreviewSource() {
    if (this.previewImgURL) {
      this.sourceURL = this.previewImgURL;
      return;
    } else if (this.dataService.colored.options != null) {
      this.sourceURL = this.dataService.colored.options['colored_url'];
      return;
    } else if (this.templateImgURL) {
      this.sourceURL = this.templateImgURL;
      return;
    }
  }


  openDialog(event): void {
    const dialogRef = this.dialog.open(EditorComponent, {
      width: '80%',
      height: '80%'
    });

    dialogRef.afterClosed().subscribe(result => {
      console.log('The dialog was closed');
    });
  }

}
