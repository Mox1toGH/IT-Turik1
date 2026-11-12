const CLOUDINARY_CLOUD_NAME = 'dzb0pjvd0'

function encodePublicId(publicId: string): string {
  return publicId.split('/').map(encodeURIComponent).join('/')
}

export function cloudinaryPhotoUrl(publicId: string, transform = 'f_webp,q_auto'): string {
  const id = encodePublicId(publicId)
  return `https://res.cloudinary.com/${CLOUDINARY_CLOUD_NAME}/image/upload/${transform}/${id}`
}
