import { accountsService } from './accounts'
import { certificatesService } from './certificates'
import { teamsService } from './teams'
import { tournamentsService } from './tournaments'

export const $api = {
  accounts: accountsService,
  certificates: certificatesService,
  teams: teamsService,
  tournaments: tournamentsService,
}
