import type { Meta, StoryObj } from '@storybook/vue3-vite'
import RoundsListSkeleton from './RoundsListSkeleton.vue'

const meta: Meta<typeof RoundsListSkeleton> = {
  title: 'Tournaments/Skeletons/Rounds list',
  component: RoundsListSkeleton,
  tags: ['autodocs'],
}

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {}
