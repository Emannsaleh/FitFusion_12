
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { FormsModule } from '@angular/forms'
import { SignupComponent } from './features/auth/pages/signup/signup.component';
import { AuthModule } from './features/auth/auth.module';
import { ProfileComponent } from "./features/auth/pages/profile/profile.component";
import { LoginComponent } from './features/auth/pages/login/login.component';
import { HomeComponent } from './home/home.component';
import { VirtualTryOnComponent } from './pages/virtual-try-on/virtual-try-on.component';
import { SharedModule } from './shared/shared.module';
import { RouterModule } from '@angular/router';
import { HomePageComponent } from './pages/home-page/home-page.component';
import { HttpClientModule } from '@angular/common/http';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MatSnackBarModule } from '@angular/material/snack-bar';


@NgModule({
  declarations: [
    AppComponent,
    // LoginComponent,
    // SignupComponent
    HomeComponent,
    VirtualTryOnComponent,
    HomePageComponent
  ],
  imports: [
    BrowserModule,
    FormsModule,
    AuthModule,
    AppRoutingModule,
    SharedModule,
    RouterModule,
    HttpClientModule,
    BrowserAnimationsModule,
    MatSnackBarModule
],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule {}




