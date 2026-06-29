
import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from 'src/app/shared/services/auth/auth.service';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';    
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss'],
})
export class LoginComponent {
  email: string = '';
  password: string = '';
  signupForm: any;
  loginForm: any;

  constructor(private router: Router,
     private authService: AuthService,
      private _formBuilder:FormBuilder ,
       private _auth:AuthService, 
       private _router:Router,
        private snackBar: MatSnackBar) {
    this.loginForm = _formBuilder.group({
      email : ['',  [Validators.required]],
      password : ['', [Validators.required, Validators.pattern(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[#$^+=!*()@%&]).{8,}$/)]]
    })
  }

 onSubmit() {
  this.authService.login({ email: this.email, password: this.password }).subscribe({
    next: () => {

      this.snackBar.open('Login successful 🎉 Welcome back!', 'Close', {
        duration: 3000,
        horizontalPosition: 'center',
        verticalPosition: 'top',
        panelClass: ['success-snackbar']
      });

      this.router.navigate(['/home']);
    },
    error: (err: any) => {
      this.snackBar.open('Login failed ❌ Check your credentials', 'Close', {
        duration: 3000,
        horizontalPosition: 'center',
        verticalPosition: 'top',
        panelClass: ['error-snackbar']
      });

      console.error(err);
    }
  });
}


  onLogin() {
    console.log('Email:', this.email);
    console.log('Password:', this.password);
    this.router.navigate(['/home']);
  }
}
