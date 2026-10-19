import type { Meta, StoryObj } from '@storybook/vue3-vite'
import { getCurrentInstance, ref } from 'vue'
import { createMemoryHistory, createRouter } from 'vue-router'
import UiTabs from './UiTabs.vue'
import UiButton from '../UiButton'

const items = [
  { value: 'overview', label: 'Overview' },
  { value: 'members', label: 'Members' },
  { value: 'tournaments', label: 'Tournaments' },
  { value: 'settings', label: 'Settings' },
]

const meta: Meta<typeof UiTabs> = {
  title: 'UI/UiTabs',
  component: UiTabs,
  tags: ['autodocs'],
  argTypes: {
    lazy: { control: 'boolean' },
    sticky: { control: 'boolean' },
    queryKey: { control: 'text' },
  },
  args: {
    items,
    lazy: true,
    sticky: false,
    queryKey: null,
  },
}

export default meta
type Story = StoryObj<typeof meta>

/** Default underline tabs; panels mount lazily and stay mounted. */
export const Default: Story = {
  render: (args) => ({
    components: { UiTabs },
    setup() {
      const active = ref('overview')
      return { args, active }
    },
    template: `
      <ui-tabs v-bind="args" v-model="active" style="max-width: 640px">
        <template #overview><p class="text-muted">Overview panel.</p></template>
        <template #members><p class="text-muted">Members panel.</p></template>
        <template #tournaments><p class="text-muted">Tournaments panel.</p></template>
        <template #settings><p class="text-muted">Settings panel.</p></template>
      </ui-tabs>
    `,
  }),
}

/** Many tabs scroll horizontally inside a narrow container. */
export const ManyTabs: Story = {
  render: (args) => ({
    components: { UiTabs },
    setup() {
      const many = Array.from({ length: 10 }, (_, i) => ({
        value: `tab-${i + 1}`,
        label: `Section ${i + 1}`,
      }))
      const active = ref('tab-1')
      return { args, many, active }
    },
    template: `
      <ui-tabs v-bind="args" :items="many" v-model="active" style="max-width: 320px">
        <template v-for="tab in many" :key="tab.value" #[tab.value]>
          <p class="text-muted">Panel {{ tab.label }}.</p>
        </template>
      </ui-tabs>
    `,
  }),
}

/** Page actions slotted at the right end of the tab bar. */
export const WithTrailing: Story = {
  render: (args) => ({
    components: { UiTabs, UiButton },
    setup() {
      const active = ref('overview')
      return { args, active }
    },
    template: `
      <ui-tabs v-bind="args" v-model="active" style="max-width: 640px">
        <template #trailing>
          <ui-button size="sm" variant="secondary">Invite</ui-button>
        </template>
        <template #overview><p class="text-muted">Overview panel.</p></template>
        <template #members><p class="text-muted">Members panel.</p></template>
        <template #tournaments><p class="text-muted">Tournaments panel.</p></template>
        <template #settings><p class="text-muted">Settings panel.</p></template>
      </ui-tabs>
    `,
  }),
}

/** Disabled tab cannot be selected; counts render as plain muted text. */
export const DisabledAndCounts: Story = {
  render: (args) => ({
    components: { UiTabs },
    setup() {
      const withMeta = [
        { value: 'overview', label: 'Overview', count: 4 },
        { value: 'members', label: 'Members', count: 12 },
        { value: 'tournaments', label: 'Tournaments', disabled: true },
        { value: 'settings', label: 'Settings' },
      ]
      const active = ref('overview')
      return { args, withMeta, active }
    },
    template: `
      <ui-tabs v-bind="args" :items="withMeta" v-model="active" style="max-width: 640px">
        <template #overview><p class="text-muted">Overview panel.</p></template>
        <template #members><p class="text-muted">Members panel.</p></template>
        <template #tournaments><p class="text-muted">Tournaments panel.</p></template>
        <template #settings><p class="text-muted">Settings panel.</p></template>
      </ui-tabs>
    `,
  }),
}

/** Active tab syncs with the route query (?tab=members) via router.replace. */
export const WithRouteSync: Story = {
  render: (args) => ({
    components: { UiTabs },
    setup() {
      const active = ref('overview')
      return { args, active }
    },
    template: `
      <ui-tabs v-bind="args" v-model="active" query-key="tab" style="max-width: 640px">
        <template #overview><p class="text-muted">Overview panel.</p></template>
        <template #members><p class="text-muted">Members panel (preselected from ?tab=members).</p></template>
        <template #tournaments><p class="text-muted">Tournaments panel.</p></template>
        <template #settings><p class="text-muted">Settings panel.</p></template>
      </ui-tabs>
    `,
  }),
  decorators: [
    (story, context) => ({
      components: { RenderedStory: story() as object },
      setup() {
        const router = createRouter({
          history: createMemoryHistory(),
          routes: [{ path: '/', component: { template: '<div />' } }],
        })
        const app = getCurrentInstance()?.appContext.app
        if (app) app.use(router)
        void router.push('/?tab=members')
        return { args: context.args }
      },
      template: '<RenderedStory v-bind="args" />',
    }),
  ],
}
