import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'
import type { AxiosError } from 'axios'
import { $api } from '@/api/services'
import { accountKeys } from '../keys'
import { computed, toValue, type MaybeRef } from 'vue'
import type {
  ActivateAccountArgs,
  ChangePasswordArgs,
  CreateRoleCodesArgs,
  CreateRoleCodesResponse,
  ForgotPasswordArgs,
  ForgotPasswordResponse,
  GetProfileResponse,
  GetRoleCodesArgs,
  GetRoleCodesResponse,
  GetUsersResponse,
  GoogleLoginArgs,
  LoginArgs,
  LoginResponse,
  RegisterArgs,
  RegisterResponse,
  ResetPasswordArgs,
  ResetPasswordResponse,
  UpdateProfileArgs,
  ValidateResetLinkArgs,
  ValidateResetLinkResponse,
} from '@/api/services/accounts/types'
import type { MutationConfig, QueryConfig } from '../types'
import type { ApiError } from '@/api/errors'

export const useProfile = (config?: QueryConfig<GetProfileResponse>) => {
  return useQuery<GetProfileResponse, AxiosError<ApiError>>({
    queryKey: accountKeys.profile(),
    queryFn: $api.accounts.getProfile,
    retry(_failureCount, error) {
      if (error.response?.status === 401) {
        return false
      }
      return true
    },
    ...config,
  })
}

export const useUsers = (config?: QueryConfig<GetUsersResponse>) => {
  return useQuery<GetUsersResponse, AxiosError<ApiError>>({
    queryKey: accountKeys.users(),
    queryFn: $api.accounts.getUsers,
    ...config,
  })
}

export const useUserById = (id: MaybeRef<number>) => {
  return useQuery<GetProfileResponse, AxiosError<ApiError>>({
    queryKey: computed(() => accountKeys.user(toValue(id))),
    queryFn: () => $api.accounts.getUserById(toValue(id)),
    enabled: computed(() => !!toValue(id)),
  })
}

export const useUpdateProfile = (
  config?: MutationConfig<
    unknown,
    AxiosError<ApiError<keyof UpdateProfileArgs['body']>>,
    UpdateProfileArgs
  >,
) => {
  return useMutation<
    unknown,
    AxiosError<ApiError<keyof UpdateProfileArgs['body']>>,
    UpdateProfileArgs
  >({
    mutationFn: $api.accounts.updateProfile,
    ...config,
  })
}

export const useDeleteAccount = (config?: MutationConfig<unknown>) => {
  return useMutation<unknown, AxiosError<ApiError>>({
    mutationFn: $api.accounts.deleteAccount,
    ...config,
  })
}

export const useActivateAccount = (
  config?: MutationConfig<unknown, AxiosError<ApiError>, ActivateAccountArgs>,
) => {
  return useMutation<unknown, AxiosError<ApiError>, ActivateAccountArgs>({
    mutationFn: $api.accounts.activateAccount,
    ...config,
  })
}

export const useChangePassword = (
  config?: MutationConfig<
    unknown,
    AxiosError<ApiError<keyof ChangePasswordArgs['body']>>,
    ChangePasswordArgs
  >,
) => {
  return useMutation<
    unknown,
    AxiosError<ApiError<keyof ChangePasswordArgs['body']>>,
    ChangePasswordArgs
  >({
    mutationFn: $api.accounts.changePassword,
    ...config,
  })
}

export const useLogin = (
  config?: MutationConfig<LoginResponse, AxiosError<ApiError>, LoginArgs>,
) => {
  return useMutation<LoginResponse, AxiosError<ApiError>, LoginArgs>({
    mutationFn: $api.accounts.login,
    ...config,
  })
}

export const useGoogleLogin = (
  config?: MutationConfig<unknown, AxiosError<ApiError>, GoogleLoginArgs>,
) => {
  return useMutation<unknown, AxiosError<ApiError>, GoogleLoginArgs>({
    mutationFn: $api.accounts.googleLogin,
    ...config,
  })
}

export const useRegister = (
  config?: MutationConfig<
    RegisterResponse,
    AxiosError<ApiError<keyof RegisterArgs['body']>>,
    RegisterArgs
  >,
) => {
  return useMutation<
    RegisterResponse,
    AxiosError<ApiError<keyof RegisterArgs['body']>>,
    RegisterArgs
  >({
    mutationFn: $api.accounts.register,
    ...config,
  })
}

export const useForgotPassword = (
  config?: MutationConfig<
    ForgotPasswordResponse,
    AxiosError<ApiError<keyof ForgotPasswordArgs['body']>>,
    ForgotPasswordArgs
  >,
) => {
  return useMutation<
    ForgotPasswordResponse,
    AxiosError<ApiError<keyof ForgotPasswordArgs['body']>>,
    ForgotPasswordArgs
  >({
    mutationFn: $api.accounts.forgotPassword,
    ...config,
  })
}

export const useResetPassword = (
  config?: MutationConfig<
    ResetPasswordResponse,
    AxiosError<ApiError<keyof ResetPasswordArgs['body']>>,
    ResetPasswordArgs
  >,
) => {
  return useMutation<
    ResetPasswordResponse,
    AxiosError<ApiError<keyof ResetPasswordArgs['body']>>,
    ResetPasswordArgs
  >({
    mutationFn: $api.accounts.resetPassword,
    ...config,
  })
}

export const useValidateResetLink = (
  payload: ValidateResetLinkArgs,
  config?: QueryConfig<ValidateResetLinkResponse>,
) => {
  return useQuery<ValidateResetLinkResponse, AxiosError<ApiError>>({
    queryKey: ['reset-link-validation', payload.token],
    queryFn: () => $api.accounts.validatePassword({ uid: payload.uid, token: payload.token }),
    ...config,
  })
}

export const useRoleCodes = (
  payload: { filter: MaybeRef<GetRoleCodesArgs['filter']> },
  config?: QueryConfig<GetRoleCodesResponse>,
) => {
  return useQuery<GetRoleCodesResponse, AxiosError<ApiError>>({
    queryKey: computed(() => accountKeys.roleCodes(toValue(payload.filter))),
    queryFn: () => $api.accounts.getRoleCodes({ filter: toValue(payload.filter) }),
    ...config,
  })
}

export const useGenerateCodes = (
  config?: MutationConfig<CreateRoleCodesResponse, AxiosError<ApiError>, CreateRoleCodesArgs>,
) => {
  const queryClient = useQueryClient()
  return useMutation<CreateRoleCodesResponse, AxiosError<ApiError>, CreateRoleCodesArgs>({
    mutationFn: $api.accounts.generateCodes,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: accountKeys.roleCodes() })
    },
    ...config,
  })
}
