import type { Meta, StoryObj } from '@storybook/vue3-vite'
import UiExpandableText from './UiExpandableText.vue'

const longText =
  'The tournament brings together student teams from twelve universities for a weekend of qualifiers, semifinals and a live final, followed by jury evaluations and an awards ceremony on Sunday evening. Teams must register before Friday midnight.'

const meta: Meta<typeof UiExpandableText> = {
  title: 'UI/UiExpandableText',
  component: UiExpandableText,
  tags: ['autodocs'],
  argTypes: {
    text: { control: 'text' },
    lines: { control: 'number', min: 1, max: 6 },
    expandLabel: { control: 'text' },
    collapseLabel: { control: 'text' },
  },
  args: {
    text: longText,
    lines: 3,
    expandLabel: 'Show more',
    collapseLabel: 'Show less',
  },
}

export default meta
type Story = StoryObj<typeof meta>

/** Short text fits: no toggle, no layout shift. */
export const ShortText: Story = {
  args: { text: 'Quarterfinals start at 10:00 in hall B.' },
  render: (args) => ({
    components: { UiExpandableText },
    setup() {
      return { args }
    },
    template: `<ui-expandable-text v-bind="args" style="max-width: 480px;" />`,
  }),
}

/** Long text clamps to 3 lines with an inline toggle. */
export const LongText: Story = {
  render: (args) => ({
    components: { UiExpandableText },
    setup() {
      return { args }
    },
    template: `<ui-expandable-text v-bind="args" style="max-width: 480px;" />`,
  }),
}

/** Long unbroken string wraps instead of overflowing. */
export const LongUnbrokenString: Story = {
  args: { text: 'registration:https://example.com/tournaments/2026/spring-split/qualifiers/group-a?team=phoenix&ref=organizer-dashboard' },
  render: (args) => ({
    components: { UiExpandableText },
    setup() {
      return { args }
    },
    template: `<ui-expandable-text v-bind="args" style="max-width: 280px;" />`,
  }),
}

/** Narrow container: the same text overflows sooner. */
export const NarrowContainer: Story = {
  render: (args) => ({
    components: { UiExpandableText },
    setup() {
      return { args }
    },
    template: `<ui-expandable-text v-bind="args" style="max-width: 220px;" />`,
  }),
}

/** Rich HTML content via the default slot (e.g. read-only editor output). */
export const RichContent: Story = {
  render: (args) => ({
    components: { UiExpandableText },
    setup() {
      return { args }
    },
    template: `
      <ui-expandable-text v-bind="args" style="max-width: 480px;">
        <h4 style="margin: 0 0 0.4rem;">Round requirements</h4>
        <p style="margin: 0 0 0.4rem;">Build a playable prototype in 48 hours. The jury scores originality, polish and teamwork.</p>
        <ul style="margin: 0; padding-left: 1.2rem;">
          <li>At least two levels</li>
          <li>Sound effects</li>
          <li>A results screen with the team name</li>
        </ul>
      </ui-expandable-text>
    `,
  }),
}
