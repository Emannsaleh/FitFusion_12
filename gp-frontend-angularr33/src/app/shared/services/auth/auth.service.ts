import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';  
import { Observable, BehaviorSubject, of, throwError } from 'rxjs';
import { tap } from 'rxjs/operators';
import { environment } from 'src/app/enviroments/enviroment';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  apiUrl = environment.apiUrl;

  private _currentUser = new BehaviorSubject<any>(null);
  currentUser$ = this._currentUser.asObservable();

  constructor(private http: HttpClient) {
    const stored = localStorage.getItem('currentUser');
    if (stored) {
      this._currentUser.next(JSON.parse(stored));
      this.initUploadSession();
    }
  }

  get currentUser() {
    return this._currentUser.value;
  }
  clearSession(): void {
  localStorage.removeItem('currentUser');
  sessionStorage.clear();

  // reset state
  this._currentUser.next(null);
}

  getCurrentUser(): Observable<any> {
    const user = this.currentUser;
    if (!user?.id) {
      return throwError(() => ({ status: 401, message: 'Not logged in' }));
    }
    return of(user);
  }
login(credentials: any): Observable<any> {
  return this.http.post<any>(`${this.apiUrl}auth/login`, credentials).pipe(
    tap(res => {
      const userData = {
        id: res.user_id,
        username: res.username,
        email: res.email,
        token: res.access_token
      };

      this._currentUser.next(userData);
      localStorage.setItem('currentUser', JSON.stringify(userData));
      this.clearUploadSessionForUser(userData.id);
      sessionStorage.setItem('uploadSessionActive', '1');
    })
  );
}

  private initUploadSession(): void {
    const user = this.currentUser;
    if (!user?.id || sessionStorage.getItem('uploadSessionActive')) {
      return;
    }

    this.clearUploadSessionForUser(user.id);
    sessionStorage.setItem('uploadSessionActive', '1');
  }

  private clearUploadSessionForUser(userId: string): void {
    this.http.delete(`${this.apiUrl}uploads/session`, {
      params: { user_id: userId }
    }).subscribe();
  }
getUserById(userId: string): Observable<any> {
  return this.http.get(`${this.apiUrl}/user/${userId}`);
}
 
  register(userData: any): Observable<any> {
    return this.http.post(`${this.apiUrl}auth/register`, userData);
  }

 logout(): Observable<any> {
  const user = this.currentUser;

  if (user?.id) {
    this.http.delete(
      `${this.apiUrl}uploads/session`,
      {
        params: { user_id: user.id }
      }
    ).subscribe();
  }

  return this.http.post(`${this.apiUrl}auth/logout`, {}).pipe(
    tap(() => {
      this.clearSession();
    })
  );
}
}