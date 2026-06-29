//import { Component, OnInit } from '@angular/core';
import {
  Component,
  OnInit,
  ViewChild,
  ElementRef
} from '@angular/core';
import { ProfileService } from 'src/app/shared/services/profile/profile.service';
import {
  bucketLabel,
  profileTypeToBucket,
  resolveClothingBucket
} from 'src/app/shared/utils/clothing-category.util';


@Component({
  selector: 'app-profile',
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.scss']
})
export class ProfileComponent implements OnInit {

  imageUrl = '';
  profileImage = '';

  selectedFile!: File;
  currentUser: any;

  activeTab = 'profile';

  userName = '';
  userEmail = '';

  tops: any[] = [];
  bottoms: any[] = [];
  shoes: any[] = [];

  @ViewChild('profileInput')
  profileInput!: ElementRef<HTMLInputElement>;

  @ViewChild('closetInput')
  closetInput!: ElementRef<HTMLInputElement>;

  selectedClosetFile!: File;
  selectedClosetType = '';

  constructor(
    private profileService: ProfileService
  ) {}

  ngOnInit(): void {

    const storedUser = localStorage.getItem('currentUser');

    if (storedUser) {

      this.currentUser = JSON.parse(storedUser);

      this.userName = this.currentUser.username || '';
      this.userEmail = this.currentUser.email || '';

      this.loadProfilePhoto();
      this.loadCloset();
    }
  }

  setActiveTab(tab: string) {
    this.activeTab = tab;
  }

  loadProfilePhoto() {

    if (!this.currentUser?.id) {
      return;
    }

    this.profileService
      .getProfilePhoto(this.currentUser.id)
      .subscribe({
        next: (res: any) => {
          this.imageUrl = res.image_url;
          this.profileImage = res.image_url;
        },
        error: () => {
          this.imageUrl = '';
          this.profileImage = '';
        }
      });
  }

  triggerProfileUpload(): void {
    this.profileInput?.nativeElement?.click();
  }
  uploadClosetItem() {

  this.profileService
    .uploadClosetItem(
      this.currentUser.id,
      this.selectedClosetFile
    )
    .subscribe({
      next: (res: any) => {
        const detectedBucket = resolveClothingBucket(res.category, res.subtype);
        const selectedBucket = profileTypeToBucket(this.selectedClosetType);

        if (detectedBucket !== selectedBucket) {
          alert(
            `This looks like ${bucketLabel(detectedBucket)}, so it was added to the ${bucketLabel(detectedBucket)} section.`
          );
        } else {
          alert('Item added successfully');
        }

        this.loadCloset();
      },
      error: (err) => {
        console.error(err);
        alert('Upload failed');
      }
    });
}
onClosetItemSelected(event: any) {

  if (!event.target.files.length) {
    return;
  }

  this.selectedClosetFile =
    event.target.files[0];

  this.uploadClosetItem();
}
  onProfileImageSelected(event: any) {

    if (event.target.files.length > 0) {

      this.selectedFile = event.target.files[0];

      this.uploadPhoto();
    }
  }

  uploadPhoto() {

    if (!this.selectedFile) {
      alert('Please select an image');
      return;
    }

    this.profileService
      .uploadProfilePhoto(
        this.currentUser.id,
        this.selectedFile
      )
      .subscribe({
        next: (res: any) => {

          this.imageUrl = res.url;
          this.profileImage = res.url;

          alert('Photo uploaded successfully');
        },
        error: (err) => {
          console.error(err);
          alert('Upload failed');
        }
      });
  }

  deletePhoto() {

    this.profileService
      .deleteProfilePhoto(this.currentUser.id)
      .subscribe({
        next: () => {

          this.imageUrl = '';
          this.profileImage = '';

          alert('Photo deleted');
        },
        error: (err) => {
          console.error(err);
        }
      });
  }

  addItem(type: string) {

  this.selectedClosetType = type;

  this.closetInput.nativeElement.click();
}

  loadCloset() {

  this.profileService
    .getClosetItems(this.currentUser.id)
    .subscribe({
      next: (res: any) => {

        this.tops = [];
        this.bottoms = [];
        this.shoes = [];

        res.items.forEach((item: any) => {
          const closetItem = {
            imageUrl: item.url,
            name: item.subtype || item.category,
            public_id: item.public_id
          };

          const bucket = resolveClothingBucket(item.category, item.subtype);

          if (bucket === 'top') {
            this.tops.push(closetItem);
          } else if (bucket === 'bottom') {
            this.bottoms.push(closetItem);
          } else {
            this.shoes.push(closetItem);
          }
        });
      },
      error: (err) => {
        console.error(err);
      }
    });
}
}