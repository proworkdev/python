import {BrowserModule} from '@angular/platform-browser';
import {NgModule} from '@angular/core';

import {AppComponent} from './app.component';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {MatButtonModule, MatCardModule, MatFormFieldModule, MatSelectModule} from '@angular/material';
import {MatDialogModule} from '@angular/material/dialog';
import {ColorPickerModule} from 'ngx-color-picker';
import {HttpClientModule} from '@angular/common/http';
import {MenuComponent} from './components/menu/menu.component';
import {TemplateEditComponent} from './components/template-edit/template-edit.component';
import {PreviewComponent} from './components/preview/preview.component';
import {MatProgressBarModule} from '@angular/material';
import { EditorComponent } from './components/editor/editor.component';
import {AngularDraggableModule} from 'angular2-draggable';

@NgModule({
  declarations: [
    AppComponent,
    MenuComponent,
    TemplateEditComponent,
    PreviewComponent,
    EditorComponent
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    ColorPickerModule,
    HttpClientModule,
    MatButtonModule,
    MatCardModule,
    MatProgressBarModule,
    MatSelectModule,
    MatDialogModule,
    MatFormFieldModule,
    AngularDraggableModule
  ],
  entryComponents: [EditorComponent],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule {
}
