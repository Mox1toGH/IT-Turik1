import { cloudinaryPhotoUrl } from '@/lib/cloudinary'
import type { SimpleIcon } from 'simple-icons'
import { siDiscord, siGithub, siInstagram, siTelegram } from 'simple-icons/icons'

export type BoardMemberLink = {
  href: string
  icon: SimpleIcon
}

export type BoardMember = {
  id: string
  name: string
  role: string
  focus: string
  description: string
  kind: string
  photoMark: string
  photo: string
  links: BoardMemberLink[]
}

export const boardMembers: BoardMember[] = [
  {
    id: '001',
    name: 'Михайло Третяк',
    role: 'Lead / Architect',
    focus: 'Backend Architecture · APIs · Core Systems',
    description: 'Led backend architecture, core APIs, and key platform systems.',
    kind: 'LEAD',
    photoMark: 'M.T.',
    photo: '',
    links: [
      {
        href: 'https://github.com/Mykhailo-Tr',
        icon: siGithub,
      },
      {
        href: 'https://www.instagram.com/tyrellw3ll1ck/',
        icon: siInstagram,
      },
      {
        href: 'https://t.me/ihmaiw2d_kc',
        icon: siTelegram,
      },
    ],
  },
  {
    id: '002',
    name: 'Балюк Денис',
    role: 'Backend / Tech Lead',
    focus: 'Notifications · Certificates · News · API Features',
    description: 'Built backend features with focus on async workflows and integrations.',
    kind: 'ENGINEERING',
    photoMark: 'D.B.',
    photo: '',
    links: [
      {
        href: 'https://github.com/Mox1toGH',
        icon: siGithub,
      },
      {
        href: 'https://www.instagram.com/mox1toua/',
        icon: siInstagram,
      },
    ],
  },
  {
    id: '003',
    name: 'Дуніна Лія',
    role: 'Project Manager',
    focus: 'Task Management · Sprint Planning · Team Coordination',
    description: 'Helped the team control tasks and sprints throughout the build',
    kind: 'CONTROL',
    photoMark: 'L.D.',
    photo: '',
    links: [
      {
        href: 'https://t.me/liyusshha',
        icon: siTelegram,
      },
      {
        href: 'https://www.instagram.com/liiahhsa/',
        icon: siInstagram,
      },
    ],
  },
  {
    id: '004',
    name: 'Муха Володимир',
    role: 'Full-Stack Lead',
    focus: 'Frontend · Backend · Architecture · Security · Performance',
    description:
      'Led frontend architecture and drove security, performance, and infrastructure improvements.',
    kind: 'LEAD',
    photoMark: 'V.M.',
    photo: cloudinaryPhotoUrl('nvugv53adeifpjltexn1'),
    links: [
      {
        href: 'https://github.com/Lastknight12',
        icon: siGithub,
      },
      {
        href: 'https://www.instagram.com/muhhaa0/',
        icon: siInstagram,
      },
      {
        href: 'https://discord.com/app',
        icon: siDiscord,
      },
      {
        href: 'https://t.me/Lastto0',
        icon: siTelegram,
      },
    ],
  },
  {
    id: '005',
    name: 'Ян Деренівський',
    role: 'Full-Stack Developer',
    focus: 'Frontend · Backend · UI Logic',
    description: 'Delivered full-stack features with focus on UI logic.',
    kind: 'ENGINEERING',
    photoMark: 'J.D.',
    photo: '',
    links: [
      {
        href: 'https://github.com/janekdeveloper',
        icon: siGithub,
      },
    ],
  },
]
