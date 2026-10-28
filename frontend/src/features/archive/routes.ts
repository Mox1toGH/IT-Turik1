export const archiveRoutes = [
  {
    path: '/terminal',
    name: 'classified-archive',
    component: () => import('./pages/ClassifiedArchivePage.vue'),
    meta: { fullscreen: true },
  },
  {
    path: '/team',
    name: 'team-investigation-board',
    component: () => import('./pages/TeamInvestigationBoardPage.vue'),
    meta: { fullscreen: true },
  },
]
