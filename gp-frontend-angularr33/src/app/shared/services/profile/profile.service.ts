import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from 'src/app/enviroments/enviroment';

@Injectable({
  providedIn: 'root'
})
export class ProfileService {

  apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getProfilePhoto(userId: string) {
    return this.http.get(
      `${this.apiUrl}get-profile-photo?user_id=${userId}`
    );
  }

  uploadProfilePhoto(userId: string, file: File) {

    const formData = new FormData();

    formData.append('user_id', userId);
    formData.append('file', file);

    return this.http.post(
      `${this.apiUrl}upload-profile-photo`,
      formData
    );
  }

  deleteProfilePhoto(userId: string) {
    return this.http.delete(
      `${this.apiUrl}delete-profile-photo?user_id=${userId}`
    );
  }

  // =========================
// CLOSET
// =========================

uploadClosetItem(userId: string, file: File) {

  const formData = new FormData();

  formData.append('file', file);

  return this.http.post(
    `${this.apiUrl}closet/items?user_id=${userId}`,
    formData
  );
}

getClosetItems(userId: string) {

  return this.http.get(
    `${this.apiUrl}closet/items?user_id=${userId}`
  );
}

deleteClosetItem(
  userId: string,
  publicId: string
) {

  return this.http.delete(
    `${this.apiUrl}closet/items/${encodeURIComponent(publicId)}?user_id=${userId}`
  );
}
}

