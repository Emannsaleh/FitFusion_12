// import { Injectable } from '@angular/core';

// @Injectable({
//   providedIn: 'root'
// })
// export class AuthService {

//   constructor() { }
// }


import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  login(email: string, password: string) {
    console.log('Logging in:', email, password);
  }

  signup(name: string, email: string, password: string) {
    console.log('Signing up:', name, email, password);
  }
}