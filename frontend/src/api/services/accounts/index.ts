import { apiClient } from '@/api/client'
import { toValue, type MaybeRefOrGetter } from 'vue'
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
import type { MaybeRefArgs } from '@/api/queries/types'
import type { UserId } from '@/api/dbTypes'

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

  async activateAccount(args: MaybeRefArgs<ActivateAccountArgs>) {
    const { data } = await apiClient.get(
      `${prefix}/activate/${toValue(args.uid)}/${toValue(args.token)}`,
    )
    return data
  },

  async updateProfile(args: MaybeRefArgs<UpdateProfileArgs>) {
    const { data } = await apiClient.patch<UpdateProfileResponse>(
      `${prefix}/profile/`,
      toValue(args.body),
    )
    return data
  },

  async forgotPassword(args: MaybeRefArgs<ForgotPasswordArgs>) {
    const { data } = await apiClient.post<ForgotPasswordResponse>(
      `${prefix}/password-reset/`,
      toValue(args.body),
    )
    return data
  },

  async resetPassword(args: MaybeRefArgs<ResetPasswordArgs>) {
    const { data } = await apiClient.post<ResetPasswordResponse>(
      `${prefix}/password-reset/${toValue(args.uid)}/${toValue(args.token)}/`,
      toValue(args.body),
    )
    return data
  },

  async validatePassword(args: MaybeRefArgs<ValidateResetLinkArgs>) {
    const { data } = await apiClient.get<ValidateResetLinkResponse>(
      `${prefix}/password-reset/${toValue(args.uid)}/${toValue(args.token)}/`,
    )
    return data
  },

  async changePassword(args: MaybeRefArgs<ChangePasswordArgs>) {
    const { data } = await apiClient.post(`${prefix}/change-password/`, toValue(args.body))
    return data
  },

  async login(args: MaybeRefArgs<LoginArgs>) {
    const { data } = await apiClient.post<LoginResponse>(`${prefix}/login/`, toValue(args.body))
    return data
  },

  async googleLogin(args: MaybeRefArgs<GoogleLoginArgs>) {
    const { data } = await apiClient.post<GoogleLoginResponse>(
      `${prefix}/google-login/`,
      toValue(args.body),
    )
    return data
  },

  async register(args: MaybeRefArgs<RegisterArgs>) {
    const { data } = await apiClient.post<RegisterResponse>(
      `${prefix}/register/`,
      toValue(args.body),
    )
    return data
  },

  async getUsers() {
    const { data } = await apiClient.get<GetUsersResponse>(`${prefix}/users`)
    return data
  },

  async getUserById(id: MaybeRefOrGetter<UserId>) {
    const { data } = await apiClient.get<GetProfileResponse>(`${prefix}/users/${toValue(id)}/`)
    return data
  },

  async getRoleCodes(args: MaybeRefArgs<GetRoleCodesArgs>) {
    const params = new URLSearchParams()
    const filter = args.filter ? toValue(args.filter) : undefined
    if (filter?.role && filter.role !== 'all') {
      params.append('role', String(filter.role))
    }
    const { data } = await apiClient.get<GetRoleCodesResponse>(`${prefix}/role-codes`, { params })
    return data
  },

  async generateCodes(args: MaybeRefArgs<CreateRoleCodesArgs>) {
    const { data } = await apiClient.post<CreateRoleCodesResponse>(
      `${prefix}/role-codes/`,
      toValue(args.body),
    )
    return data
  },
}
