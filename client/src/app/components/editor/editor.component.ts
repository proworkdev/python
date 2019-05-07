import {Component, Inject, ViewChild, ElementRef, OnInit, HostListener} from '@angular/core';
import {DataService} from '../../services/data.service';
import {MatDialogRef, MAT_DIALOG_DATA} from '@angular/material';
import {ApiService} from '../../services/api.service';

@Component({
  selector: 'app-editor',
  templateUrl: './editor.component.html',
  styleUrls: ['./editor.component.css']
})

export class EditorComponent implements OnInit {
  currentDesignURL = null;
  position: any;

  @ViewChild('myImage') myImage: ElementRef;
  @ViewChild('range') range: ElementRef;
  @ViewChild('cropZone') cropZone: ElementRef;

  scaledMargin = 0;
  width: number;

  templateID = null;

  scale = 1;
  offsetX = 0;
  offsetY = 0;

  editZoneWidth: number;
  editZoneHeight: number;
  startEditZoneWidth: number;
  startEditZoneHeight: number;

  constructor(
    public apiService: ApiService,
    public dataService: DataService,
    public dialogRef: MatDialogRef<EditorComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any) {
    if (this.dataService.design.options) {
      this.currentDesignURL = this.dataService.design.options['design_url'];
    }
    this.dataService.design.$options.subscribe((new_value) => {
      this.currentDesignURL = new_value;
    });
    this.processTemplateData(this.dataService.template);
  }

  processTemplateData(data) {
    const editZone = data.options['edit-zone'];

    if (!editZone) {
      return;
    }

    this.startEditZoneWidth = editZone[0];
    this.startEditZoneHeight = editZone[1];
    this.editZoneWidth = editZone[0];
    this.editZoneHeight = editZone[1];
    this.templateID = data['filename'];
    this.resizeCropZone();
  }

  @HostListener('window:resize')
  resizeCropZone() {
    const ratio = this.startEditZoneWidth / this.startEditZoneHeight;

    console.log('111111111');
    console.log(window.innerWidth + ' x ' + window.innerHeight);
    console.log(ratio);
    console.log();
    console.log('editZoneWidth: ', this.editZoneWidth, 'editZoneHeight: ', this.editZoneHeight);

    if (this.startEditZoneWidth >= this.startEditZoneHeight) {
      this.editZoneHeight = window.innerHeight * 0.6 * ratio;
      this.editZoneWidth = window.innerWidth * 0.6;
    } else {
      this.editZoneWidth = window.innerHeight * ratio * 0.6;
      this.editZoneHeight = window.innerHeight * 0.6;
    }
  }

  imageScale() {
    const newValue = this.range.nativeElement.value;
    if (newValue !== this.scale) {
      this.scale = newValue / 100;
    }
  }

  onNoClick(): void {
    this.dialogRef.close();
    console.log(this.range.nativeElement.value);
  }

  onMoveEnd(event) {
    this.position = event;
    const x = event.x;
    const y = event.y;
    const original_width = this.myImage.nativeElement.naturalWidth;
    const original_height = this.myImage.nativeElement.naturalHeight;
    const current_width = this.myImage.nativeElement.width;
    const current_height = this.myImage.nativeElement.height;
    const ratio_width = original_width / current_width;
    const ratio_height = original_height / current_height;
    const offset_x = x * ratio_width;
    const offset_y = y * ratio_height;
    this.offsetX = offset_x;
    this.offsetY = offset_y;
  }

  processImage(event) {
    const edits = {
      'offset_x': this.offsetX,
      'offset_y': this.offsetY,
      'scale': this.scale
    };
    const design_id = this.dataService.design.options['design_filename'];
    const template_id = this.dataService.template.options['identifier'];
    this.apiService.processDesign(design_id, template_id, this.dataService.pickColor, edits);
    this.dialogRef.close();
  }

  testButtonClicked(event) {
    console.log(this.editZoneWidth);
    console.log(this.editZoneHeight);
  }

  ngOnInit() {
    console.log('image element:', this.myImage);
    console.log('crop zone element: ', this.cropZone);
  }
}
