import { Component, OnInit } from '@angular/core';
import {
  RecommendationService,
  UploadItem,
  ClosetItem
} from 'src/app/shared/services/recommendation/recommendation.service';
import { environment } from 'src/app/enviroments/enviroment';
import {
  bucketLabel,
  bucketToApiCategory,
  ClothingBucket,
  resolveClothingBucket
} from 'src/app/shared/utils/clothing-category.util';

interface DisplayItem {
  id?: number;
  public_id?: string;
  image: string;
  name: string;
  type: string;
  color?: string;
  gender?: string;
  season?: string;
  usage?: string;
  category?: string;
}

@Component({
  selector: 'app-recommendation',
  templateUrl: './recommendation.component.html',
  styleUrls: ['./recommendation.component.scss']
})
export class RecommendationComponent implements OnInit {

  userId = '';

  uploads: UploadItem[] = [];
  closetItems: ClosetItem[] = [];

  tops: DisplayItem[] = [];
  bottoms: DisplayItem[] = [];
  shoes: DisplayItem[] = [];

  closetTops: DisplayItem[] = [];
  closetBottoms: DisplayItem[] = [];
  closetShoes: DisplayItem[] = [];

  loadingRecommendations = false;
  showRecommendations = false;

  recommendedOutfit: DisplayItem[] = [];
  activeTab: 'upload' | 'closet' = 'upload';

  showAddItemModal = false;
  editingItemId: number | null = null;
  editingPublicId: string | null = null;
  editingSource: 'upload' | 'closet' = 'upload';
  selectedImage = '';
  showToast = false;
  toastMessage = '';

  newItem = {
    name: '',
    type: '',
    color: '',
    gender: '',
    season: '',
    occasion: ''
  };

  selectedOccasion = 'any';

  constructor(
    private recommendationService: RecommendationService
  ) {}

  ngOnInit(): void {
    const storedUser = localStorage.getItem('currentUser');
    if (storedUser) {
      this.userId = JSON.parse(storedUser).id || '';
    }

    if (!this.userId) {
      return;
    }

    this.loadUploads();
    this.loadCloset();
  }

  setTab(tab: 'upload' | 'closet'): void {
    this.activeTab = tab;
    this.showRecommendations = false;

    if (tab === 'upload') {
      this.loadUploads();
    } else {
      this.loadCloset();
    }
  }

  loadUploads(): void {
    this.recommendationService.getUploads(this.userId).subscribe({
      next: (response) => {
        this.uploads = response.items.filter(item => item.source === 'upload');
        this.tops = this.uploads
          .filter(x => resolveClothingBucket(x.category, x.subtype) === 'top')
          .map(item => this.toDisplayItem(item));
        this.bottoms = this.uploads
          .filter(x => resolveClothingBucket(x.category, x.subtype) === 'bottom')
          .map(item => this.toDisplayItem(item));
        this.shoes = this.uploads
          .filter(x => resolveClothingBucket(x.category, x.subtype) === 'foot')
          .map(item => this.toDisplayItem(item));
      },
      error: err => console.error(err)
    });
  }

  loadCloset(): void {
    this.recommendationService.getClosetItems(this.userId).subscribe({
      next: (response) => {
        this.closetItems = response.items;

        this.recommendationService.getUploads(this.userId).subscribe({
          next: (uploadResponse) => {
            const closetUploads = uploadResponse.items.filter(
              item => item.source === 'closet'
            );
            this.categorizeClosetItems(closetUploads);
          },
          error: (err) => {
            this.categorizeClosetItems([]);
            console.error(err);
          }
        });
      },
      error: err => console.error(err)
    });
  }

  private categorizeClosetItems(closetUploads: UploadItem[]): void {
    const uploadByPublicId = new Map<string, UploadItem>();

    closetUploads.forEach((upload) => {
      const publicId = this.resolveUploadPublicId(upload);
      if (publicId) {
        uploadByPublicId.set(publicId, upload);
      }
    });

    this.closetTops = this.closetItems
      .filter(x => resolveClothingBucket(x.category, x.subtype) === 'top')
      .map(item => this.toClosetDisplayItem(item, uploadByPublicId.get(item.public_id)));
    this.closetBottoms = this.closetItems
      .filter(x => resolveClothingBucket(x.category, x.subtype) === 'bottom')
      .map(item => this.toClosetDisplayItem(item, uploadByPublicId.get(item.public_id)));
    this.closetShoes = this.closetItems
      .filter(x => resolveClothingBucket(x.category, x.subtype) === 'foot')
      .map(item => this.toClosetDisplayItem(item, uploadByPublicId.get(item.public_id)));
  }

  onImageSelected(event: Event, slot: ClothingBucket): void {
    const input = event.target as HTMLInputElement;
    const files = input.files;

    if (!files || files.length === 0) {
      return;
    }

    Array.from(files).forEach((file) => {
      this.recommendationService
        .addUploadItem(this.userId, 'upload', file)
        .subscribe({
          next: (created) => this.handleUploadedItem(created, slot),
          error: err => console.error(err)
        });
    });

    input.value = '';
  }

  private handleUploadedItem(created: UploadItem, slot: ClothingBucket): void {
    const detectedBucket = resolveClothingBucket(created.category, created.subtype);

    if (detectedBucket === slot) {
      this.loadUploads();
      return;
    }

    this.recommendationService
      .updateUploadItem(this.userId, created.id, {
        category: bucketToApiCategory(detectedBucket)
      })
      .subscribe({
        next: () => {
          this.showToastMessage(
            `This looks like ${bucketLabel(detectedBucket)}, so it was moved to the correct section.`
          );
          this.loadUploads();
        },
        error: (err) => {
          console.error(err);
          this.loadUploads();
        }
      });
  }

  getRecommendation(): void {
    this.loadingRecommendations = true;
    this.showRecommendations = false;

    const useCloset = this.activeTab === 'closet';

    this.recommendationService
      .getOutfitRecommendation(
        this.userId,
        this.selectedOccasion,
        useCloset
      )
      .subscribe({
        next: (response) => {
          this.loadingRecommendations = false;
          this.showRecommendations = true;
          this.recommendedOutfit = [];

          if (response.top) {
            this.recommendedOutfit.push(this.toDisplayItem(response.top));
          }
          if (response.bottom) {
            this.recommendedOutfit.push(this.toDisplayItem(response.bottom));
          }
          if (response.shoes) {
            this.recommendedOutfit.push(this.toDisplayItem(response.shoes));
          }
        },
        error: err => {
          this.loadingRecommendations = false;
          this.showToastMessage(
            err?.error?.detail || 'Could not generate outfit. Add tops, bottoms, and shoes first.'
          );
          console.error(err);
        }
      });
  }

  deleteItem(item: DisplayItem): void {
    if (!item.id) {
      return;
    }

    this.recommendationService
      .deleteUploadItem(this.userId, item.id)
      .subscribe({
        next: () => this.loadUploads(),
        error: err => console.error(err)
      });
  }

  editClosetItem(item: DisplayItem): void {
    if (!item.public_id) {
      return;
    }

    this.editingSource = 'closet';
    this.editingItemId = item.id ?? null;
    this.editingPublicId = item.public_id;
    this.selectedImage = item.image;
    this.newItem = {
      name: item.name || '',
      type: item.type || '',
      color: item.color || '',
      gender: item.gender || '',
      season: item.season || '',
      occasion: this.mapUsageToOccasion(item.usage)
    };
    this.showAddItemModal = true;
  }

  editItem(item: DisplayItem): void {
    if (!item.id) {
      return;
    }

    this.editingSource = 'upload';
    this.editingPublicId = null;
    this.editingItemId = item.id;
    this.selectedImage = item.image;
    this.newItem = {
      name: item.name || '',
      type: item.type || '',
      color: item.color || '',
      gender: item.gender || '',
      season: item.season || '',
      occasion: this.mapUsageToOccasion(item.usage)
    };
    this.showAddItemModal = true;
  }

  saveItem(): void {
    if (this.editingSource === 'closet') {
      this.saveClosetItem();
      return;
    }

    if (!this.editingItemId) {
      return;
    }

    const payload = this.buildItemUpdatePayload();

    this.recommendationService
      .updateUploadItem(this.userId, this.editingItemId, payload)
      .subscribe({
        next: () => {
          this.showToastMessage('Item updated successfully');
          this.closeAddItem();
          this.loadUploads();
        },
        error: (err) => {
          console.error(err);
          this.showToastMessage('Failed to update item');
        }
      });
  }

  private saveClosetItem(): void {

  if (!this.editingPublicId) {
    return;
  }

  const payload = this.buildItemUpdatePayload();

  this.recommendationService
    .updateClosetItem(
      this.editingPublicId,
      payload
    )
    .subscribe({
      next: () => {

        this.showToastMessage(
          'Item updated successfully'
        );

        this.closeAddItem();

        this.loadCloset();
      },
      error: (err) => {

        console.error(err);

        this.showToastMessage(
          'Failed to update item'
        );
      }
    });
}

  closeAddItem(): void {
    this.showAddItemModal = false;
    this.editingItemId = null;
    this.editingPublicId = null;
    this.editingSource = 'upload';
    this.selectedImage = '';
    this.newItem = {
      name: '',
      type: '',
      color: '',
      gender: '',
      season: '',
      occasion: ''
    };
  }

  addItem(): void {
    this.saveItem();
  }

  get isEditingItem(): boolean {
    return this.editingItemId !== null || this.editingPublicId !== null;
  }

  private buildItemUpdatePayload(): {
    type?: string;
    color?: string;
    gender?: string;
    season?: string;
    usage?: string;
  } {
    const payload: {
      type?: string;
      color?: string;
      gender?: string;
      season?: string;
      usage?: string;
    } = {};

    if (this.newItem.type || this.newItem.name) {
      payload.type = this.newItem.type || this.newItem.name;
    }
    if (this.newItem.color && this.newItem.color !== 'Select color') {
      payload.color = this.newItem.color;
    }
    if (this.newItem.gender && this.newItem.gender !== 'Select gender') {
      payload.gender = this.newItem.gender;
    }
    if (this.newItem.season && this.newItem.season !== 'Select season') {
      payload.season = this.newItem.season;
    }

    const usage = this.mapOccasionToUsage(this.newItem.occasion);
    if (usage) {
      payload.usage = usage;
    }

    return payload;
  }

  private resolveUploadPublicId(upload: UploadItem): string {
    return upload.cloudinary_public_id || (upload as UploadItem & { public_id?: string }).public_id || '';
  }

  private mapOccasionToUsage(occasion: string): string | undefined {
    const map: Record<string, string> = {
      Casual: 'Casual',
      Business: 'Smart Casual',
      Formal: 'Formal',
      Party: 'Party',
      Athletic: 'Sports',
      Beach: 'Casual',
      'Any Occasion': ''
    };

    const usage = map[occasion];
    return usage || undefined;
  }

  private mapUsageToOccasion(usage?: string): string {
    if (!usage) {
      return '';
    }

    const map: Record<string, string> = {
      Casual: 'Casual',
      'Smart Casual': 'Business',
      Formal: 'Formal',
      Party: 'Party',
      Sports: 'Athletic',
      Ethnic: 'Formal'
    };

    return map[usage] || usage;
  }

  get closetItemCount(): number {
    return this.closetTops.length + this.closetBottoms.length + this.closetShoes.length;
  }

  private toDisplayItem(item: any): DisplayItem {
    return {
      id: item.id,
      public_id: item.cloudinary_public_id || item.public_id,
      image: this.resolveImageUrl(item),
      name: item.subtype || item.category || 'Item',
      type: item.subtype || item.category || '',
      color: item.color,
      gender: item.gender,
      season: item.season,
      usage: item.usage,
      category: item.category
    };
  }

  private toClosetDisplayItem(item: ClosetItem, upload?: UploadItem): DisplayItem {
    return {
      id: upload?.id,
      public_id: item.public_id,
      image: item.url,
      name: upload?.subtype || item.subtype || item.category || 'Item',
      type: upload?.subtype || item.subtype || item.category || '',
      color: upload?.color || item.color,
      gender: upload?.gender || item.gender,
      season: upload?.season || item.season,
      usage: upload?.usage || item.usage,
      category: upload?.category || item.category
    };
  }

  private resolveImageUrl(item: any): string {
    const url = item.image_url || item.url || item.image || '';
    if (!url) {
      return '';
    }
    if (url.startsWith('http')) {
      return url;
    }
    const base = environment.apiUrl.replace(/\/$/, '');
    return url.startsWith('/') ? `${base}${url}` : `${base}/${url}`;
  }

  private showToastMessage(message: string): void {
    this.toastMessage = message;
    this.showToast = true;
    setTimeout(() => {
      this.showToast = false;
    }, 3000);
  }
}
