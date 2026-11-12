import { nextTick, onUnmounted, ref } from 'vue'

type ArchiveTerminalOptions = {
  reducedMotion: boolean
  openFolder: (name: string) => boolean
}

const initialMessage = '...WHO OPENED THE ARCHIVE?'

export function useArchiveTerminal(options: ArchiveTerminalOptions) {
  const command = ref('')
  const terminalLines = ref<string[]>([])
  const terminalOutput = ref<HTMLElement | null>(null)
  const typedMessage = ref('')
  const isUserTyping = ref(false)

  let typeTimer: ReturnType<typeof setInterval> | undefined
  let userTypingTimer: ReturnType<typeof setTimeout> | undefined

  function appendLines(lines: string[]) {
    terminalLines.value.push(...lines)
    nextTick(() => {
      if (terminalOutput.value) terminalOutput.value.scrollTop = terminalOutput.value.scrollHeight
    })
  }

  function typeMessage(message: string) {
    if (typeTimer) clearInterval(typeTimer)
    typedMessage.value = ''

    if (options.reducedMotion) {
      typedMessage.value = message
      return
    }

    let index = 0
    typeTimer = setInterval(() => {
      typedMessage.value = message.slice(0, ++index)
      if (index >= message.length && typeTimer) clearInterval(typeTimer)
    }, 72)
  }

  function executeCommand(raw: string) {
    const tokens = raw.trim().split(/\s+/)
    const action = (tokens.shift() || '').toLowerCase()
    const argument = tokens
      .join(' ')
      .replace(/\.dat$/i, '')
      .toUpperCase()
    if (action !== 'clear') appendLines([`> ${raw}`])
    switch (action) {
      case 'help':
        appendLines(['TRY: FOLDERS, OPEN SWITZERLAND, ABOUT, STATUS, CLEAR.'])
        break
      case 'folders':
        appendLines([
          'FOUND DIRECTORIES // INDEX 01',
          'SWITZERLAND/  CAMP/  UNCLASSIFIED/  CORRUPTED/',
        ])
        break
      case 'open': {
        if (options.openFolder(argument)) {
          appendLines([`DIRECTORY ${argument}/ MOUNTED.`])
          break
        }
        appendLines([`! UNKNOWN COMMAND: ${raw}`, 'No matching directory was mounted. Try HELP.'])
        break
      }
      case 'about':
        appendLines([
          'NORTHSTAR FIELD SYSTEM // ARCHIVE NODE 09',
          'Recovered shared photographs from field sessions.',
          'Origin metadata: incomplete. Some images were not in the original index.',
        ])
        break
      case 'status':
        appendLines([
          'DISK 01: MOUNTED',
          'SIGNAL: PRESENT',
          'ARCHIVE INTEGRITY: PARTIAL',
          'OPERATOR: UNCONFIRMED',
        ])
        break
      case 'clear':
        terminalLines.value = []
        break
      default:
        appendLines([`! UNKNOWN COMMAND: ${raw}`, 'The machine returns no useful error. Try HELP.'])
    }
  }

  function submitCommand() {
    const raw = command.value.trim()
    if (!raw) return
    command.value = ''
    executeCommand(raw)
  }

  function registerUserTyping() {
    isUserTyping.value = true
    if (userTypingTimer) clearTimeout(userTypingTimer)
    userTypingTimer = setTimeout(() => (isUserTyping.value = false), 850)
  }

  function start() {
    terminalLines.value = [
      'FOUND ARCHIVE // DIRECTORY INDEX',
      'FOUR PHOTO DIRECTORIES RECOVERED.',
      'SELECT A FOLDER OR TYPE FOLDERS.',
    ]
    typeMessage(initialMessage)
  }

  function stop() {
    if (typeTimer) clearInterval(typeTimer)
    if (userTypingTimer) clearTimeout(userTypingTimer)
  }

  onUnmounted(stop)

  return {
    command,
    terminalLines,
    terminalOutput,
    typedMessage,
    isUserTyping,
    appendLines,
    submitCommand,
    registerUserTyping,
    start,
  }
}
