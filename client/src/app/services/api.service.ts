import {Injectable} from '@angular/core';
import {HttpClient, HttpEvent, HttpEventType, HttpParams} from '@angular/common/http';
import {Subject} from 'rxjs';
import {environment} from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ApiService {

  $download_request = null;

  uploadedPercentage = 0;

  isUploading = false;
  isUploaded = false;
  isProcessed = false;

  filename = null;
  resultUrl = null;

  templateData = new Subject<any>();
  availableTemplates = new Subject<any>();
  coloredData = new Subject<any>();
  designData = new Subject<any>();
  previewData = new Subject<any>();
  downloadData = new Subject<any>();

  relativeAPIURL = environment.api_base_url;

  constructor(private http: HttpClient) {
    console.log(environment.api_base_url);
  }

  uploadDesign(file) {
    this.isUploaded = false;
    this.isProcessed = false;
    const uploadData = new FormData();
    if (file) {
      uploadData.append('design', file, file.name);
    }
    this.http.post(this.relativeAPIURL + '/design-upload', uploadData, {
      reportProgress: true,
      observe: 'events'
    }).subscribe((event: HttpEvent<any>) => {
        switch (event.type) {
          case HttpEventType.Sent:
            console.log('sent');
            this.isUploaded = true;
            break;
          case HttpEventType.Response:
            console.log(event);
            this.processUploadedDesignResponse(event.body);
            break;
          case 1: {
            if (Math.round(this.uploadedPercentage) !== Math.round(event['loaded'] / event['total'] * 100)) {
              this.uploadedPercentage = event['loaded'] / event['total'] * 100;
            }
            break;
          }
        }
      },
      error => {
        console.log(error);
        this.resetFile();
      });
  }

  processColoredData(data) {
    this.coloredData.next(data);
  }

  processTemplateData(data) {
    this.templateData.next(data);
  }

  processAvailableTemplates(data) {
    this.availableTemplates.next(data);
  }

  processUploadedDesignResponse(data) {
    this.designData.next(data);
  }

  processProcessedDesignResponse(data) {
    this.isProcessed = true;
    this.previewData.next(data);
    this.checkDownload(data['download']['filename']);
  }

  processDesign(design_id, template_id, color, edits) {
    const uploadData = new FormData();
    uploadData.append('design_id', design_id);
    uploadData.append('template_id', template_id);
    uploadData.append('colorize_color', color);
    uploadData.append('edits', JSON.stringify(edits));

    this.http.post(this.relativeAPIURL + '/design-process', uploadData, {
      reportProgress: true,
      observe: 'events'
    }).subscribe((event: HttpEvent<any>) => {
        switch (event.type) {
          case HttpEventType.Sent:
            console.log('sent');
            break;
          case HttpEventType.Response:
            console.log(event);
            this.processProcessedDesignResponse(event.body);
            break;
          case 1: {
            if (Math.round(this.uploadedPercentage) !== Math.round(event['loaded'] / event['total'] * 100)) {
              this.uploadedPercentage = event['loaded'] / event['total'] * 100;
            }
            break;
          }
        }
      },
      error => {
        console.log(error);
        this.resetFile();
      });
  }

  getTemplateOptions(template_id) {
    const postData = new FormData();
    postData.append('template_id', template_id);
    this.http.post(this.relativeAPIURL + '/template-cfg', postData, {}).subscribe((response) => {
      this.processTemplateData(response);
    }, (error1 => {
      console.log(error1);
    }));
  }

  getAvailableTemplates() {
    this.http.get(this.relativeAPIURL + '/templates-available').subscribe((response) => {
      this.processAvailableTemplates(response);
    });
  }

  getColoredTemplate(template_id, color) {
    const postData = new FormData();
    postData.append('template_id', template_id);
    postData.append('colorize_color', color);
    this.http.post(this.relativeAPIURL + '/template-colored', postData, {}).subscribe((response) => {
      this.processColoredData(response);
    }, (error1 => {
      console.log(error1);
    }));
  }

  checkDownload(download_filename) {
    const postData = new FormData();
    postData.append('download_filename', download_filename);
    this.$download_request = this.http.post(this.relativeAPIURL + '/check-dnl', postData, {})
      .subscribe((data) => {
        console.log('exists: ' + data['exists']);
        this.downloadData.next(data);
      }, error1 => {
        console.log('DOWNLOAD ERROR: ' + error1);
      });
  }

  resetFile() {
    this.uploadedPercentage = 0;

    this.isUploading = false;
    this.isUploaded = false;
    this.isProcessed = false;

    this.filename = null;
    this.resultUrl = null;
  }
}
