import { apiClient } from '@/api/client'

const prefix = '/api/accounts/google-calendar'

export interface GoogleCalendarStatusResponse {
    connected: boolean
}

export interface GoogleCalendarConnectResponse {
    auth_url: string
}

export interface GoogleCalendarCallbackArgs {
    code: string
}

export interface ExportToGoogleCalendarArgs {
    event_ids?: number[]
    round_ids?: number[]
}

export interface ExportedItem {
    type: 'event' | 'round'
    id: number
    google_event_id?: string
    google_event_ids?: string[]
    html_link?: string
}

export interface ExportToGoogleCalendarResponse {
    created: ExportedItem[]
    errors: { type: string; id: number; error: string }[]
}

export const googleCalendarService = {
    async getStatus() {
        const { data } = await apiClient.get<GoogleCalendarStatusResponse>(`${prefix}/status/`)
        return data
    },

    async connect() {
        const { data } = await apiClient.post<GoogleCalendarConnectResponse>(`${prefix}/connect/`)
        return data
    },

    async callback(args: GoogleCalendarCallbackArgs) {
        const { data } = await apiClient.post<GoogleCalendarStatusResponse>(`${prefix}/callback/`, {
            code: args.code,
        })
        return data
    },

    async disconnect() {
        const { data } = await apiClient.post<GoogleCalendarStatusResponse>(`${prefix}/disconnect/`)
        return data
    },

    async exportToGoogle(args: ExportToGoogleCalendarArgs) {
        const { data } = await apiClient.post<ExportToGoogleCalendarResponse>(
            '/api/tournaments/my-calendar/export-to-google/',
            args,
        )
        return data
    },
}
