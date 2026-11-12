export interface BoardNote {
  id: string
  text: string
  x: number
  y: number
  rotation: number
  hand: 'hand-one' | 'hand-two' | 'hand-three' | 'typed'
  struck?: boolean
}

export const boardNotes: BoardNote[] = [
  { id: 'still-watching', text: 'still watching', x: 74, y: 300, rotation: -8, hand: 'hand-one' },
  { id: 'not-yet', text: 'not yet', x: 914, y: 285, rotation: 7, hand: 'hand-two', struck: true },
  { id: 'counted-four', text: 'four on record', x: 82, y: 474, rotation: -90, hand: 'typed' },
  {
    id: 'count-fixed',
    text: 'who fixed the count',
    x: 915,
    y: 574,
    rotation: -5,
    hand: 'hand-three',
  },
  { id: 'leave-room', text: 'leave room', x: 380, y: 77, rotation: -3, hand: 'typed' },
  {
    id: 'left-running',
    text: 'someone left it running',
    x: 82,
    y: 116,
    rotation: -5,
    hand: 'hand-two',
  },
  { id: 'watches-back', text: 'it watches back', x: 930, y: 109, rotation: 6, hand: 'hand-one' },
  {
    id: 'unclaimed-signal',
    text: 'signal without a name',
    x: 1042,
    y: 385,
    rotation: 88,
    hand: 'typed',
    struck: true,
  },
  { id: 'hum-remains', text: 'still humming', x: 75, y: 617, rotation: 3, hand: 'hand-three' },
  {
    id: 'machine-on',
    text: 'the machine is still running',
    x: 927,
    y: 626,
    rotation: -4,
    hand: 'hand-two',
  },
  {
    id: 'signal-uk',
    text: 'nobody claimed the signal',
    x: 71,
    y: 190,
    rotation: -88,
    hand: 'typed',
  },
  {
    id: 'answer-not-here',
    text: 'the answer is elsewhere',
    x: 1015,
    y: 179,
    rotation: 4,
    hand: 'hand-three',
    struck: true,
  },
  { id: 'only-index', text: 'only an index', x: 443, y: 650, rotation: -2, hand: 'hand-one' },
  { id: 'click-here', text: 'click here? sure.', x: 1068, y: 464, rotation: 9, hand: 'hand-two' },
]

export const uvBoardNotes: BoardNote[] = [
  { id: 'north-coordinate', text: '17° 04′ N', x: 95, y: 335, rotation: 0, hand: 'typed' },
  { id: 'west-coordinate', text: '44° 12′ W', x: 960, y: 337, rotation: 0, hand: 'typed' },
  { id: 'unopened', text: 'RETURN IT UNOPENED', x: 485, y: 640, rotation: 0, hand: 'typed' },
  { id: 'gaze', text: 'hold your gaze on it', x: 64, y: 544, rotation: -8, hand: 'hand-two' },
  { id: 'eye', text: 'press and hold the eye', x: 874, y: 537, rotation: 7, hand: 'typed' },
  {
    id: 'field-computer',
    text: 'find the field computer',
    x: 295,
    y: 92,
    rotation: -4,
    hand: 'hand-one',
  },
  {
    id: 'real-file',
    text: 'the real file is on the computer',
    x: 782,
    y: 94,
    rotation: 5,
    hand: 'typed',
  },
  {
    id: 'behind-it',
    text: 'behind what you keep looking at',
    x: 450,
    y: 671,
    rotation: -2,
    hand: 'hand-three',
    struck: true,
  },
]

export interface PinnedBoardNote {
  id: string
  text: string
  detail: string
  placement: 'note-top' | 'note-index' | 'note-eye'
}

export const pinnedBoardNotes: PinnedBoardNote[] = [
  {
    id: 'machine',
    text: 'the machine is still warm',
    detail: 'no one remembers the switch',
    placement: 'note-top',
  },
  {
    id: 'index',
    text: 'this is only an index',
    detail: 'the complete file is elsewhere',
    placement: 'note-index',
  },
  {
    id: 'eye',
    text: 'the signal begins at the eye',
    detail: 'the computer waits behind it',
    placement: 'note-eye',
  },
]

export const tapeNoteClue = {
  front: 'UNDER THE STATIC',
  back: 'THE SIGNAL COMES FROM THE MACHINE.',
}
