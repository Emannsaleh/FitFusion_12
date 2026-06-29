export type ClothingBucket = 'top' | 'bottom' | 'foot';

export function resolveClothingBucket(category?: string, subtype?: string): ClothingBucket {
  const cat = `${category || ''} ${subtype || ''}`.toLowerCase().trim();

  if (
    cat.includes('bottom') ||
    cat.includes('lower') ||
    cat.includes('pant') ||
    cat.includes('jean') ||
    cat.includes('skirt') ||
    cat.includes('short') ||
    cat.includes('trouser') ||
    cat.includes('legging')
  ) {
    return 'bottom';
  }

  if (cat.includes('foot') || cat.includes('shoe') || cat.includes('sneaker') || cat.includes('boot')) {
    return 'foot';
  }

  if (
    cat.includes('top') ||
    cat.includes('upper') ||
    cat.includes('shirt') ||
    cat.includes('blouse') ||
    cat.includes('jacket') ||
    cat.includes('hoodie') ||
    cat.includes('sweater')
  ) {
    return 'top';
  }

  return 'top';
}

export function bucketToApiCategory(bucket: ClothingBucket): string {
  return bucket;
}

export function profileTypeToBucket(type: string): ClothingBucket {
  const map: Record<string, ClothingBucket> = {
    tops: 'top',
    bottoms: 'bottom',
    shoes: 'foot'
  };

  return map[type] || 'top';
}

export function bucketLabel(bucket: ClothingBucket): string {
  if (bucket === 'foot') {
    return 'shoes';
  }

  return `${bucket}s`;
}
