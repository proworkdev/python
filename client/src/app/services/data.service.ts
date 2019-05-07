import {Injectable, OnInit} from '@angular/core';
import {ApiService} from './api.service';
import {Subject} from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class DataService {

  templateURL = new Subject<string>();
  previewURL = new Subject<string>();
  downloadURL = new Subject<string>();
  designURL = new Subject<string>();
  designUploaded = new Subject<string>();

  lastTemplateURL = null;

  pickColor = '#FFF';

  templates_available = {
    $changed: new Subject<any>(),
    templates_list: []
  };

  template = {
    template_id: null,
    options: null,
    $template_id: new Subject<any>(),
    $options: new Subject<any>()
  };

  colored = {
    template_id: null,
    options: null,
    $template_id: new Subject<any>(),
    $options: new Subject<any>()
  };

  design = {
    options: null,
    $options: new Subject<any>()
  };

  preview = {
    template_id: new Subject<any>(),
    options: null,
    $options: new Subject<any>(),
    $reset: new Subject<any>()
  };

  download = {
    options: null,
    $options: new Subject<any>()
  };

  constructor(private apiService: ApiService) {
    this.apiService.designData.subscribe((data) => {
      this.processDesignData(data);
    });
    this.apiService.templateData.subscribe((data) => {
      this.processTemplateData(data);
    });
    this.apiService.downloadData.subscribe((data) => {
      this.download.options = data;
      this.download.$options.next(data);
    });
    this.apiService.previewData.subscribe((data) => {
      this.preview.options = data;
      this.preview.$options.next(data);
    });
    this.apiService.coloredData.subscribe((data) => {
      this.processColoredData(data);
    });
    this.apiService.availableTemplates.subscribe((data) => {
      this.templates_available.templates_list = data['templates'];
      this.templates_available.$changed.next(data);
    });
    this.apiService.getAvailableTemplates();
  }

  processDesignData(data: any) {
    console.log('Got design data:');
    this.design.options = data['options'];
    this.design.$options.next(data);
  }

  processColoredData(data: any) {
    const template_id = data['template_id'];
    const options = data['options'];
    this.colored.template_id = template_id;
    this.colored.options = options;
    this.colored.$template_id.next(template_id);
    this.colored.$options.next(options);
  }

  processTemplateData(data: any) {
    const template_id = data['template_id'];
    console.log(data);
    const options = data['options'];
    this.template.template_id = template_id;
    this.template.options = options;
    this.template.$template_id.next(template_id);
    this.template.$options.next(options);
  }

  resetPreview() {
    this.previewURL.next(null);
    this.preview.options = null;
    this.preview.$options.next(null);
    this.preview.$reset.next(null);
  }

  resetDownload() {
    this.apiService.downloadData.next(null);
  }
}
