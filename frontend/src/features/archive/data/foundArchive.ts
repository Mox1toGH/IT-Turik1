import { cloudinaryPhotoUrl } from '@/lib/cloudinary'

export type ArchivePhotoFile = {
  id: string
  filename: string
  src: string
  thumb: string
  title: string
  description: string
  locked?: boolean
  corrupted?: boolean
}

export type ArchiveFolder = {
  id: string
  name: string
  description: string
  files: ArchivePhotoFile[]
}

export const PHOTO_PLACEHOLDER_SRC = '/archive/photos/photo-placeholder.svg'

const placeholder = {
  src: PHOTO_PLACEHOLDER_SRC,
  thumb: PHOTO_PLACEHOLDER_SRC,
  title: 'placeholder',
  description: 'description',
}
const thumbnailTransform = 'f_webp,q_auto,w_480,h_360,c_limit'

function teamPhotos(
  photos: (Pick<ArchivePhotoFile, 'id'> & Partial<ArchivePhotoFile>)[],
): ArchivePhotoFile[] {
  return photos.map((photo) => {
    return {
      id: photo.id,
      filename: photo.filename ?? `${photo.id}.webp`,
      title: photo.title ?? placeholder.title,
      description: photo.description ?? placeholder.description,
      src: photo.src ?? cloudinaryPhotoUrl(photo.id),
      thumb: photo.thumb ?? cloudinaryPhotoUrl(photo.id, thumbnailTransform),
      locked: photo.locked,
      corrupted: photo.corrupted ?? false,
    }
  })
}

const switzerlandTeamPhotos = teamPhotos([
  { id: 'tvh6hu8lmmyvoscsemwt' },
  { id: 'piuzgeblvvgispma6rhu' },
  { id: 'm4ksje6yvjwb6kdwn3ie' },
  { id: 'b1xqzc2837nwue3xmftp' },
  { id: 'prjvlrdodoh3qu2vxbcz' },
  { id: 'mcssmkfyctetkqhgdhbk' },
  { id: 'qlpueubichsmsorfqua1' },
  { id: 'cdz6y79aelx7fxijxr73' },
  { id: 'xpghdckx0pek7egejvj2' },
  { id: 'wgxfpjftho7yqe0jqcrt' },
  { id: 'igangs4rqu1wbed4a4ic' },
  { id: 'm1v9rh3jlipq79bdypzo' },
  { id: 'bd9ez3d2jmyk3zje9ibq' },
  { id: 'banmwpjen4tp2ykz6d4k' },
  { id: 'bqjjmjhavq1rlv9kxcwp' },
  { id: 'qayqftu2992onm3jrhyw' },
  { id: 'netuygp52ek4dqmycwjw' },
])

const campTeamPhotos = teamPhotos([
  { id: 'mmbjw676ietywf0vmkg3' },
  { id: 'ljjuy7ffhmci5fo61toq' },
  { id: 'm6ifitb3uj59bwsqcvzv' },
  { id: 'xaob9vzbptzcz9sxir1i' },
  { id: 'qpxidzztmgzf2a6zy9hb' },
  { id: 'obluykw6o6yadxfookak' },
  { id: 'yumhydvul57xpewj77jd' },
  { id: 'mnyzpsreejkljfsmwsdl' },
  { id: 't7o34f66eqz95msvnm50' },
  { id: 'ryvrzldgcywapxzyksue' },
  { id: 'xitpy2mzygazldrzfkig' },
  { id: 'iueepsmyaexmydt0zm2d' },
  { id: 'fkcdctwouig2xl2plei1' },
  { id: 'we9u0k9irapyhh9d8k5z' },
  { id: 'povpznniwsgbu0dgehlj' },
])

const corruptedPhotos = teamPhotos([
  {
    id: '▓▒░-c0rrupt-0̸0̷3̴1̶-⟁',
    filename: 'F̷R̸▓M▒E_0̸0̷3̴1̶.в̷i̸n̴',
    src: cloudinaryPhotoUrl('mmbjw676ietywf0vmkg3'),
    thumb: placeholder.thumb,
    title: '▓▒░⟊⟟⧖⟁̷̸ ̴R̷E̸C̴O̷R̸D̴ ̵L̸O̷S̴T̸ ░▒▓',
    description: 'Three frames were removed before the file was damaged.',
    locked: true,
    corrupted: true,
  },
  {
    id: '⟁-c0rrupt-1̸1̷8̴0̶-░▒▓',
    filename: 'U̷N̸T▒T̴L̷E̸D_1̸1̷8̴0̶.r̸a̷w̴',
    src: cloudinaryPhotoUrl('ljjuy7ffhmci5fo61toq'),
    thumb: placeholder.thumb,
    title: '⧖⟁▓▒░⟟̴ ̷S̸U̴B̷J̸E̴C̷T̸ U̷N̸K̴N̷O̸W̴N̷ ▓▒░',
    description: 'The file timestamp predates the storage device.',
    locked: true,
    corrupted: true,
  },
])

const unclassifiedTeamPhotos = teamPhotos([{ id: 'p6rj2kvktqtwzucb8cia' }])

export const archiveFolders: ArchiveFolder[] = [
  {
    id: 'switzerland',
    name: 'SWITZERLAND',
    description: 'Transit records / alpine region',
    files: [...switzerlandTeamPhotos],
  },
  {
    id: 'camp',
    name: 'CAMP',
    description: 'Outdoor session / equipment check',
    files: [...campTeamPhotos],
  },
  {
    id: 'unclassified',
    name: 'UNCLASSIFIED',
    description: 'Loose material / source pending',
    files: [...unclassifiedTeamPhotos],
  },
  {
    id: 'corrupted',
    name: 'CORRUPTED',
    description: 'Damaged records / authentication required',
    files: corruptedPhotos,
  },
]
