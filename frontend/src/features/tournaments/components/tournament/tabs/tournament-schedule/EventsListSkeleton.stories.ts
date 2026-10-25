import type { Meta, StoryObj } from '@storybook/vue3-vite'
import EventsListSkeleton from './EventsListSkeleton.vue'

const meta: Meta<typeof EventsListSkeleton> = {
  title: 'Tournaments/Skeletons/Events list',
  component: EventsListSkeleton,
  tags: ['autodocs'],
}

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {}
