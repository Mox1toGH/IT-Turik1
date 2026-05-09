import { accountsService } from './accounts'
import { evaluationService } from './evaluation'
import { teamsService } from './teams'
import { tournamentsService } from './tournaments'

export const $api = {
  accounts: accountsService,
  teams: teamsService,
  tournaments: tournamentsService,
  evaluation: evaluationService,
}
