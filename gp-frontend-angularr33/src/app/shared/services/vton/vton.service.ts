import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { environment } from 'src/app/enviroments/enviroment';

@Injectable({
  providedIn: 'root'
})
export class VtonService {

  apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  createVton(data: FormData): Observable<any> {
    return this.http.post(`${this.apiUrl}predict/post`, data);
  }

  getVtonData(): Observable<Blob> {
    return this.http.get(`${this.apiUrl}predict/get`, { responseType: 'blob' });
  }

  fetchImageAsFile(
    url: string,
    filename = 'image.jpg'
  ): Observable<File> {
    return this.http.get(url, { responseType: 'blob' }).pipe(
      map(blob => new File(
        [blob],
        filename,
        { type: blob.type || 'image/jpeg' }
      ))
    );
  }
}
