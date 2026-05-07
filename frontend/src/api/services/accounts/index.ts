import { apiClient } from '@/api/client'
import type {
  ForgotPasswordResponse,
  CreateRoleCodesResponse,
  GetProfileResponse,
  GetRoleCodesResponse,
  GetUsersResponse,
  GoogleLoginResponse,
  LoginResponse,
  RegisterResponse,
  ResetPasswordResponse,
  UpdateProfileResponse,
  UpdateProfileArgs,
  ForgotPasswordArgs,
  ResetPasswordArgs,
  ValidateResetLinkArgs,
  ChangePasswordArgs,
  LoginArgs,
  GoogleLoginArgs,
  RegisterArgs,
  GetRoleCodesArgs,
  CreateRoleCodesArgs,
  ValidateResetLinkResponse,
  ActivateAccountArgs,
} from './types'

const prefix = '/api/accounts'

export const accountsService = {
  async getProfile() {
    const { data } = await apiClient.get<GetProfileResponse>(`${prefix}/profile`)
    return data
  },

  async deleteAccount() {
    const { data } = await apiClient.delete(`${prefix}/profile/`)
    return data
  },

  async activateAccount(args: ActivateAccountArgs) {
    const { data } = await apiClient.get(`${prefix}/activate/${args.uid}/${args.token}`)
    return data
  },

  async updateProfile(args: UpdateProfileArgs) {
    const { data } = await apiClient.patch<UpdateProfileResponse>(`${prefix}/profile/`, args.body)
    return data
  },

  async forgotPassword(args: ForgotPasswordArgs) {
    const { data } = await apiClient.post<ForgotPasswordResponse>(
      `${prefix}/password-reset/`,
      args.body,
    )
    return data
  },

  async resetPassword(args: ResetPasswordArgs) {
    const { data } = await apiClient.post<ResetPasswordResponse>(
      `${prefix}/password-reset/${args.uid}/${args.token}/`,
      args.body,
    )
    return data
  },

  async validatePassword(args: ValidateResetLinkArgs) {
    const { data } = await apiClient.get<ValidateResetLinkResponse>(
      `${prefix}/password-reset/${args.uid}/${args.token}/`,
    )
    return data
  },

  async changePassword(args: ChangePasswordArgs) {
    const { data } = await apiClient.post(`${prefix}/change-password/`, args.body)
    return data
  },

  async login(args: LoginArgs) {
    const { data } = await apiClient.post<LoginResponse>(`${prefix}/login/`, args.body)
    return data
  },

  async googleLogin(args: GoogleLoginArgs) {
    const { data } = await apiClient.post<GoogleLoginResponse>(`${prefix}/google-login/`, args.body)
    return data
  },

  async register(args: RegisterArgs) {
    const { data } = await apiClient.post<RegisterResponse>(`${prefix}/register/`, args.body)
    return data
  },

  async getUsers() {
    const { data } = await apiClient.get<GetUsersResponse>(`${prefix}/users`)
    return data
  },

  async getUserById(id: number) {
    const { data } = await apiClient.get<GetProfileResponse>(`${prefix}/users/${id}/`)
    return data
  },

  async getRoleCodes(args: GetRoleCodesArgs) {
    const params = new URLSearchParams()
    if (args.filter?.role && args.filter.role !== 'all') {
      params.append('role', String(args.filter.role))
    }
    const { data } = await apiClient.get<GetRoleCodesResponse>(`${prefix}/role-codes`, { params })
    return data
  },

  async generateCodes(args: CreateRoleCodesArgs) {
    const { data } = await apiClient.post<CreateRoleCodesResponse>(
      `${prefix}/role-codes/`,
      args.body,
    )
    return data
  },
}
