import {Component, Input, OnInit, Output} from '@angular/core';
import {ApiService} from '../../services/api.service';
import {DataService} from '../../services/data.service';

@Component({
  selector: 'app-menu',
  templateUrl: './menu.component.html',
  styleUrls: ['./menu.component.css']
})
export class MenuComponent implements OnInit {

  color = '#FFF';
  current_file = null;
  current_template = null;
  download_disabled = true;

  template_list = [];

  show_colorpicker = false;

  constructor(public apiService: ApiService, public dataService: DataService) {
    this.dataService.download.$options.subscribe(() => {
      if (this.dataService.download && this.dataService.download.options) {
        this.download_disabled = !this.dataService.download.options['exists'];
      }
    });
    this.dataService.templates_available.$changed.subscribe((data) => {
      this.template_list = this.dataService.templates_available.templates_list;
    });
    this.dataService.template.$options.subscribe(() => {
      this.show_colorpicker = this.dataService.template.options && this.dataService.template.options['colorizable']['color_mask'];
    });
  }

  onFileChanged(event) {
    this.onDelete(false);
    this.current_file = event.target.files[0];
    this.apiService.uploadDesign(this.current_file);
    event.srcElement.value = null;
  }

  onTemplateChanged($event) {
    console.log('ON TEMPLATE CHANGED');
    const template_id = $event.value;
    this.current_template = template_id;
    this.apiService.getTemplateOptions(template_id);
    this.color = null;
    this.onDelete();
    this.dataService.resetPreview();
  }

  onDelete(resetColor?) {
    if (resetColor == null) {
      resetColor = true;
    }
    if (this.apiService.$download_request) {
      this.apiService.$download_request.unsubscribe();
      this.apiService.$download_request = null;
    }
    if (resetColor) {
      this.color = null;
    }
    this.current_file = null;
    this.apiService.resetFile();
    this.dataService.resetPreview();
    this.dataService.resetDownload();
    this.download_disabled = true;
  }

  pickColor(event): void {
    this.current_file = null;
    this.download_disabled = true;
    this.dataService.resetPreview();
    this.dataService.downloadURL = null;
    this.dataService.download.options = null;
    this.dataService.pickColor = event;
    this.apiService.getColoredTemplate(this.current_template, event);
  }

  downloadFile() {
    if (this.dataService.download.options && this.dataService.download.options['exists']) {
      const download_url = this.dataService.download.options['url'];
      window.open(download_url);
    } else {
      alert('no download url available :( it may be a bug');
    }
  }

  ngOnInit() {
  }

}
