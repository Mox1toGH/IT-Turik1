const GOOGLE_SCRIPT_SRC = 'https://accounts.google.com/gsi/client'

export interface GoogleCredentialResponse {
  credential: string
  select_by: string
}

export const loadGoogleScript = () => {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  if ((window as any).google?.accounts?.id) {
    return Promise.resolve()
  }

  return new Promise<void>((resolve, reject) => {
    const existingScript = document.querySelector(`script[src="${GOOGLE_SCRIPT_SRC}"]`)
    if (existingScript) {
      existingScript.addEventListener('load', () => resolve(), { once: true })
      existingScript.addEventListener(
        'error',
        () => reject(new Error('Google script load failed')),
        { once: true },
      )
      return
    }

    const script = document.createElement('script')
    script.src = GOOGLE_SCRIPT_SRC
    script.async = true
    script.defer = true
    script.onload = () => resolve()
    script.onerror = () => reject(new Error('Google script load failed'))
    document.head.appendChild(script)
  })
}

interface RenderGoogleButtonOptions {
  container: HTMLElement
  clientId: string
  callback: (response: GoogleCredentialResponse) => void
  width?: number
}

export const renderGoogleButton = async ({
  container,
  clientId,
  callback,
  width = 340,
}: RenderGoogleButtonOptions) => {
  if (!container) {
    throw new Error('Google button container is missing')
  }

  if (!clientId) {
    throw new Error('VITE_GOOGLE_CLIENT_ID is missing')
  }

  await loadGoogleScript()

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const google = (window as any).google?.accounts?.id

  if (!google) {
    throw new Error('Google API not available')
  }

  google.initialize({
    client_id: clientId,
    callback,
  })

  container.innerHTML = ''
  google.renderButton(container, {
    type: 'standard',
    theme: 'outline',
    size: 'large',
    shape: 'pill',
    text: 'continue_with',
    width,
    logo_alignment: 'left',
  })
}
