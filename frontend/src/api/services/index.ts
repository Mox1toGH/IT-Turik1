import { accountsService } from './accounts'
import { certificatesService } from './certificates'
import { newsService } from './news'
import { evaluationSerice } from './evaluation'
import { teamsService } from './teams'
import { tournamentsService } from './tournaments'
import { pointsService } from './points'

export const $api = {
  accounts: accountsService,
  certificates: certificatesService,
  news: newsService,
  teams: teamsService,
  tournaments: tournamentsService,
  evaluation: evaluationSerice,
  points: pointsService,
}
