import { Component } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { AuthService } from '../services/auth/auth.service';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.scss']
})
export class NavbarComponent {
  isLoginPage = false;

  constructor(private router: Router, private authService: AuthService, private snackBar: MatSnackBar) {}

  ngOnInit(): void {
  this.isLoginPage =
  this.router.url.startsWith('/login') ||
  this.router.url.startsWith('/signup');

  this.router.events.subscribe(event => {
  if (event instanceof NavigationEnd) {
    this.isLoginPage =
      event.urlAfterRedirects.startsWith('/login') ||
      event.urlAfterRedirects.startsWith('/signup');
  }
});
}

signOut() {
  this.authService.logout().subscribe({
    next: () => {
      this.snackBar.open('Logged out successfully ✅', 'Close', {
        duration: 3000,
        panelClass: ['success-snackbar']
      });

      this.router.navigate(['/login']);
    },
    error: () => {
      this.authService.clearSession();

      this.snackBar.open('Logged out successfully ✅', 'Close', {
        duration: 3000,
        panelClass: ['success-snackbar']
      });

      this.router.navigate(['/login']);
    }
  });
}
}