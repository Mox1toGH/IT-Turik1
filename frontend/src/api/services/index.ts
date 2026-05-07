import { accountsService } from './accounts'
import { teamsService } from './teams'
import { tournamentsService } from './tournaments'

export const $api = {
  accounts: accountsService,
  teams: teamsService,
  tournaments: tournamentsService,
}
