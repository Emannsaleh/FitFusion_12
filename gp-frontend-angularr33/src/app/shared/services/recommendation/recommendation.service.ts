import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from 'src/app/enviroments/enviroment';

export interface ClosetItem {
  public_id: string;
  url: string;
  category?: string;
  subtype?: string;
  gender?: string;
  season?: string;
  usage?: string;
  color?: string;
}

export interface UploadItem {
  id: number;
  file_path?: string;
  image_url: string;
  category: string;
  subtype?: string;
  gender?: string;
  season?: string;
  usage?: string;
  color?: string;
  cloudinary_public_id?: string | null;
  cloudinary_url?: string | null;
  source: 'upload' | 'closet';
}

@Injectable({
  providedIn: 'root'
})
export class RecommendationService {

  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  // ==================== CLOSET ====================

  getClosetItems(userId: string): Observable<{ items: ClosetItem[] }> {
    const params = new HttpParams().set('user_id', userId);

    return this.http.get<{ items: ClosetItem[] }>(
      `${this.apiUrl}closet/items`,
      { params }
    );
  }

  addClosetItem(
    userId: string,
    file: File
  ): Observable<any> {

    const formData = new FormData();
    formData.append('file', file);

    const params = new HttpParams()
      .set('user_id', userId);

    return this.http.post(
      `${this.apiUrl}closet/items`,
      formData,
      { params }
    );
  }

  deleteClosetItem(
    userId: string,
    publicId: string
  ): Observable<any> {

    const params = new HttpParams()
      .set('user_id', userId);

    return this.http.delete(
      `${this.apiUrl}closet/items/${encodeURIComponent(publicId)}`,
      { params }
    );
  }

  updateClosetItem(
  publicId: string,
  updated: any
) {

  return this.http.put(
    `${this.apiUrl}closet/items/${encodeURIComponent(publicId)}`,
    updated
  );
}

  // ==================== UPLOADS ====================

  getUploads(
    userId: string
  ): Observable<{ items: UploadItem[] }> {

    const params = new HttpParams()
      .set('user_id', userId);

    return this.http.get<{ items: UploadItem[] }>(
      `${this.apiUrl}uploads/items`,
      { params }
    );
  }

  addUploadItem(
    userId: string,
    source: 'upload' | 'closet',
    file?: File,
    publicId?: string
  ): Observable<UploadItem> {

    const formData = new FormData();

    if (file) {
      formData.append('file', file);
    }

    if (publicId) {
      formData.append('public_id', publicId);
    }

    const params = new HttpParams()
      .set('user_id', userId)
      .set('source', source);

    return this.http.post<UploadItem>(
      `${this.apiUrl}uploads/items`,
      formData,
      { params }
    );
  }

  updateUploadItem(
    userId: string,
    itemId: number,
    updated: Partial<UploadItem>
  ): Observable<UploadItem> {

    const params = new HttpParams()
      .set('user_id', userId);

    return this.http.put<UploadItem>(
      `${this.apiUrl}uploads/items/${itemId}`,
      updated,
      { params }
    );
  }

  deleteUploadItem(
    userId: string,
    itemId: number
  ): Observable<any> {

    const params = new HttpParams()
      .set('user_id', userId);

    return this.http.delete(
      `${this.apiUrl}uploads/items/${itemId}`,
      { params }
    );
  }

  // ==================== CLEAR TEMP UPLOADS ====================

  clearUploadSession(
    userId: string
  ): Observable<any> {

    const params = new HttpParams()
      .set('user_id', userId);

    return this.http.delete(
      `${this.apiUrl}uploads/session`,
      { params }
    );
  }

  // ==================== RECOMMENDATION ====================

  getOutfitRecommendation(
    userId: string,
    usage?: string,
    useCloset: boolean = false
  ): Observable<any> {

    let params = new HttpParams()
      .set('user_id', userId)
      .set('use_closet', useCloset.toString());

    const mappedUsage = this.mapUsage(usage);
    if (mappedUsage) {
      params = params.set('usage', mappedUsage);
    }

    return this.http.get(
      `${this.apiUrl}generate/outfit`,
      { params }
    );
  }

  private mapUsage(usage?: string): string | undefined {
    if (!usage || usage === 'any') {
      return undefined;
    }

    const usageMap: Record<string, string> = {
      casual: 'Casual',
      ethnic: 'Ethnic',
      formal: 'Formal',
      party: 'Party',
      smart_casual: 'Smart Casual',
      sports: 'Sports'
    };

    return usageMap[usage] ?? usage;
  }
}