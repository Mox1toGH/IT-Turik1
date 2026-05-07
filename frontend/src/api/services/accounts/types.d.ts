import type { RoleActivationCode, Team, User } from '@/api/dbTypes'

export type GetProfileResponse = User & {
  teams: Pick<Team, 'id' | 'name' | 'contact_discord' | 'contact_telegram'>[]
}

export type UpdateProfileBody = Pick<User, 'username' | 'full_name' | 'phone' | 'city'>
export interface UpdateProfileArgs {
  body: UpdateProfileBody
}
export type UpdateProfileResponse = UpdateProfileBody & Pick<User, 'role'>

export interface ForgotPasswordBody {
  email: string
}
export interface ForgotPasswordArgs {
  body: ForgotPasswordBody
}
export interface ForgotPasswordResponse {
  message: string
}

export interface ResetPasswordBody {
  new_password: string
  confirm_password: string
}
export interface ResetPasswordArgs {
  uid: string
  token: string
  body: ResetPasswordBody
}
export interface ResetPasswordResponse {
  message: string
}

export interface ValidateResetLinkArgs {
  uid: string
  token: string
}
export type ValidateResetLinkResponse = ResetPasswordResponse

export interface ChangePasswordBody {
  current_password: string
  new_password: string
  confirm_password: string
}
export interface ChangePasswordArgs {
  body: ChangePasswordBody
}
export interface ChangePasswordResponse {
  message: string
}

interface LoginBody {
  username: User['username']
  password: string
}
export interface LoginArgs {
  body: LoginBody
}
export interface LoginResponse {
  access: string
  refresh: string
  onboarding_required: boolean
}

export interface GoogleLoginBody {
  credential: string
}
export interface GoogleLoginArgs {
  body: GoogleLoginBody
}
export type GoogleLoginResponse = LoginResponse & {
  user: User
}

export interface RegisterBody {
  username: string
  email: string
  password: string
  role: string
  redeem_code: string
  full_name: string
  phone: string
  city: string
}
export interface RegisterArgs {
  body: RegisterBody
}
export type RegisterResponse = {
  access: string
  refresh: string
  onboarding_required: boolean
}

export type GetUsersResponse = Pick<User, 'id' | 'username' | 'email' | 'full_name' | 'role'>[]

export type ActivationCode =
  | ({ is_used: false } & Pick<RoleActivationCode, 'id' | 'code' | 'role' | 'created_at'> & {
        created_by_username: string
      })
  | ({
      is_used: true
    } & Pick<RoleActivationCode, 'id' | 'code' | 'role' | 'created_at' | 'used_at'> & {
        used_by: User['username']
        created_by_username: string
        used_by_username: string
      })

export interface GetRoleCodesFilter {
  role?: Omit<User['role'], 'team'> | 'all'
}
export interface GetRoleCodesArgs {
  filter?: GetRoleCodesFilter
}
export type RoleCodesUserRole = Extract<User['role'], 'admin' | 'jury' | 'organizer'>
export type GetRoleCodesResponse = {
  codes: ActivationCode[]
  active_counts: Record<RoleCodesUserRole, number>
}

interface CreateRoleCodesBody {
  role: string
  quantity: number
}
export interface CreateRoleCodesArgs {
  body: CreateRoleCodesBody
}
export type CreateRoleCodesResponse = Pick<GetRoleCodesResponse, 'active_counts'> & {
  created: ActivationCode[]
  active_counts: Record<RoleCodesUserRole, number>
}

export interface ActivateAccountArgs {
  uid: string
  token: string
}
