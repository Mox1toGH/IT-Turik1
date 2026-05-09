import { accountsService } from './accounts'
import { certificatesService } from './certificates'
import { newsService } from './news'
import { teamsService } from './teams'
import { tournamentsService } from './tournaments'

export const $api = {
  accounts: accountsService,
  certificates: certificatesService,
  news: newsService,
  teams: teamsService,
  tournaments: tournamentsService,
}
