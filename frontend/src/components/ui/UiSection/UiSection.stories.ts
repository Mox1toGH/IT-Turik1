import type { Meta, StoryObj } from '@storybook/vue3-vite'
import UiSection from './UiSection.vue'
import UiButton from '../UiButton'

const meta: Meta<typeof UiSection> = {
  title: 'UI/UiSection',
  component: UiSection,
  tags: ['autodocs'],
  argTypes: {
    title: { control: 'text' },
    description: { control: 'text' },
    divider: { control: 'boolean' },
  },
  args: {
    title: 'Members',
    description: 'Search accepted members, requests, and invitations.',
    divider: false,
  },
}

export default meta
type Story = StoryObj<typeof meta>

/** Plain section: title, description and content, no box. */
export const Default: Story = {
  render: (args) => ({
    components: { UiSection },
    setup() {
      return { args }
    },
    template: `
      <ui-section v-bind="args">
        <p class="text-muted">Section content sits directly on the page background.</p>
      </ui-section>
    `,
  }),
}

/** Section with actions slotted at the right of the title. */
export const WithActions: Story = {
  render: (args) => ({
    components: { UiSection, UiButton },
    setup() {
      return { args }
    },
    template: `
      <ui-section v-bind="args">
        <template #actions>
          <ui-button size="sm" variant="secondary">Invite</ui-button>
        </template>
        <p class="text-muted">Actions stay next to the title, not inside a card header.</p>
      </ui-section>
    `,
  }),
}

/** Divider variant: sections separated by a hairline. */
export const WithDivider: Story = {
  args: { divider: true },
  render: (args) => ({
    components: { UiSection },
    setup() {
      return { args }
    },
    template: `
      <div style="display: grid; gap: 2.5rem;">
        <ui-section title="Overview" description="Always visible summary." />
        <ui-section v-bind="args">
          <p class="text-muted">Second section separated by a top border.</p>
        </ui-section>
      </div>
    `,
  }),
}

/** Title only, no description. */
export const TitleOnly: Story = {
  args: { title: 'Standings', description: undefined },
  render: (args) => ({
    components: { UiSection },
    setup() {
      return { args }
    },
    template: `
      <ui-section v-bind="args">
        <p class="text-muted">Content without a description line.</p>
      </ui-section>
    `,
  }),
}
