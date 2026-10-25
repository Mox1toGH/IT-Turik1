import type { Meta, StoryObj } from '@storybook/vue3-vite'
import UiTruncate from './UiTruncate.vue'

const longTitle =
  'International University Championship of Programming and Design Systems Finals 2026'

const meta: Meta<typeof UiTruncate> = {
  title: 'UI/UiTruncate',
  component: UiTruncate,
  tags: ['autodocs'],
  argTypes: {
    text: { control: 'text' },
    lines: { control: 'number', min: 1, max: 6 },
    tooltip: { control: 'boolean' },
  },
  args: {
    text: longTitle,
    lines: 1,
    tooltip: true,
  },
}

export default meta
type Story = StoryObj<typeof meta>

/** Short text fits: no ellipsis, no tooltip. */
export const ShortText: Story = {
  args: { text: 'Team Phoenix' },
  render: (args) => ({
    components: { UiTruncate },
    setup() {
      return { args }
    },
    template: `<ui-truncate v-bind="args" style="max-width: 480px;" />`,
  }),
}

/** Long title in a narrow container: ellipsis + tooltip only when truncated. */
export const LongText: Story = {
  render: (args) => ({
    components: { UiTruncate },
    setup() {
      return { args }
    },
    template: `<ui-truncate v-bind="args" style="max-width: 220px;" />`,
  }),
}

/** Long unbroken string wraps instead of breaking the layout. */
export const LongUnbrokenString: Story = {
  args: { text: 'superlongteamnamewithoutanyspacesorbreaks Sight2026finals@example.com' },
  render: (args) => ({
    components: { UiTruncate },
    setup() {
      return { args }
    },
    template: `<ui-truncate v-bind="args" style="max-width: 220px;" />`,
  }),
}

/** Multi-line clamp (3 lines) with tooltip on truncation. */
export const MultiLine: Story = {
  args: {
    lines: 3,
    text: 'The tournament brings together student teams from twelve universities for a weekend of qualifiers, semifinals and a live final, followed by jury evaluations and an awards ceremony on Sunday evening.',
  },
  render: (args) => ({
    components: { UiTruncate },
    setup() {
      return { args }
    },
    template: `<ui-truncate v-bind="args" style="max-width: 280px;" />`,
  }),
}

/** Rich content via the default slot. */
export const RichContent: Story = {
  render: (args) => ({
    components: { UiTruncate },
    setup() {
      return { args }
    },
    template: `
      <ui-truncate v-bind="args" style="max-width: 220px;">
        <strong>Team Phoenix</strong> — champions of the spring split
      </ui-truncate>
    `,
  }),
}
