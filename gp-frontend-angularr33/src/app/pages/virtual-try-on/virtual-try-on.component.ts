import { Component, OnInit } from '@angular/core';
import { VtonService } from 'src/app/shared/services/vton/vton.service';
import { AuthService } from 'src/app/shared/services/auth/auth.service';
import { ProfileService } from 'src/app/shared/services/profile/profile.service';

@Component({
  selector: 'app-virtual-try-on',
  templateUrl: './virtual-try-on.component.html',
  styleUrls: ['./virtual-try-on.component.scss']
})
export class VirtualTryOnComponent implements OnInit {

  profilePreview: string | null = null;
  itemPreview: string | null = null;
  selectedCategory = '';
  profileFile?: File;
  itemFile?: File;
  resultImage = '';

  readonly categoryMap: Record<string, string> = {
    dress: 'dresses',
    top: 'upper_body',
    bottom: 'lower_body',
    bag: 'bag'
  };

  showResult = false;
  loadingVton = false;
  userId = '';

  constructor(
    private vtonService: VtonService,
    private authService: AuthService,
    private profileService: ProfileService
  ) {}

  ngOnInit(): void {
    const user = this.authService.currentUser;
    if (!user?.id) {
      return;
    }

    this.userId = user.id;
    this.loadSavedProfilePhoto();
  }

  loadSavedProfilePhoto(): void {
    this.profileService.getProfilePhoto(this.userId).subscribe({
      next: (res: any) => {
        const imageUrl = res?.image_url;
        if (!imageUrl) {
          return;
        }

        this.profilePreview = imageUrl;
        this.vtonService.fetchImageAsFile(imageUrl, 'profile.jpg').subscribe({
          next: (file) => {
            this.profileFile = file;
          },
          error: () => {
            this.profilePreview = null;
          }
        });
      }
    });
  }

  onProfileUpload(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) {
      return;
    }

    this.profileFile = file;

    const reader = new FileReader();
    reader.onload = () => {
      this.profilePreview = reader.result as string;
    };
    reader.readAsDataURL(file);
    input.value = '';
  }

  onItemUpload(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) {
      return;
    }

    this.itemFile = file;

    const reader = new FileReader();
    reader.onload = () => {
      this.itemPreview = reader.result as string;
    };
    reader.readAsDataURL(file);
    input.value = '';
  }

  tryItOn(): void {
    if (!this.profileFile) {
      alert('Upload your photo first');
      return;
    }

    if (!this.itemFile || !this.selectedCategory) {
      alert('Upload item and select a type first');
      return;
    }

    const backendCategory = this.categoryMap[this.selectedCategory];
    if (!backendCategory) {
      alert('Invalid item type selected');
      return;
    }

    const formData = new FormData();
    formData.append('person_image', this.profileFile);
    formData.append('cloth_image', this.itemFile);
    formData.append('category', backendCategory);

    this.loadingVton = true;
    this.showResult = false;
    this.resultImage = '';

    this.vtonService.createVton(formData).subscribe({
      next: () => this.pollVtonResult(),
      error: (err) => {
        this.loadingVton = false;
        alert(err?.error?.detail || 'Try-on failed to start');
      }
    });
  }

  private pollVtonResult(attempt = 0): void {
    const maxAttempts = 150;
    const delayMs = 5000;

    this.vtonService.getVtonData().subscribe({
      next: (blob: Blob) => {
        this.loadingVton = false;
        this.resultImage = URL.createObjectURL(blob);
        this.showResult = true;
      },
      error: () => {
        if (attempt < maxAttempts) {
          setTimeout(() => this.pollVtonResult(attempt + 1), delayMs);
        } else {
          this.loadingVton = false;
          alert('Try-on is still processing. Please try again in a few minutes.');
        }
      }
    });
  }
}
