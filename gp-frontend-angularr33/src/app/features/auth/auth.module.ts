// import { NgModule } from '@angular/core';
// import { CommonModule } from '@angular/common';

// import { AuthRoutingModule } from './auth-routing.module';
// import { LoginComponent } from './pages/login/login.component';
// import { SignupComponent } from './pages/signup/signup.component';


// @NgModule({
//   declarations: [
//     LoginComponent,
//     SignupComponent
//   ],
//   imports: [
//     CommonModule,
//     AuthRoutingModule
//   ]
// })
// export class AuthModule { }


import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { LoginComponent } from './pages/login/login.component';
import { SignupComponent } from './pages/signup/signup.component';
import { AuthRoutingModule } from './auth-routing.module';
import { RouterModule } from '@angular/router';
import { ProfileComponent } from './pages/profile/profile.component';
import { BrowserModule } from '@angular/platform-browser';
import { RecommendationComponent } from '../../pages/recommendation/recommendation.component';
import { SharedModule } from '../../shared/shared.module';

@NgModule({
  declarations: [
    LoginComponent,
    SignupComponent,
    RecommendationComponent,
    ProfileComponent
  ],
  imports: [
    CommonModule,
    FormsModule,
    AuthRoutingModule,
    RouterModule,
    SharedModule
    // BrowserModule
  ],
  exports:[
    SignupComponent,
    LoginComponent,
    RecommendationComponent,
    ProfileComponent
  ]
})
export class AuthModule {}




