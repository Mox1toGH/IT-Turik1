import type { Meta, StoryObj } from '@storybook/vue3-vite'
import SubmissionsListSkeleton from './SubmissionsListSkeleton.vue'

const meta: Meta<typeof SubmissionsListSkeleton> = {
  title: 'Tournaments/Skeletons/Submissions list',
  component: SubmissionsListSkeleton,
  tags: ['autodocs'],
}

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {}
