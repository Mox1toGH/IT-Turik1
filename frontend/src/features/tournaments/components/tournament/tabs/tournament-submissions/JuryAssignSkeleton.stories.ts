import type { Meta, StoryObj } from '@storybook/vue3-vite'
import JuryAssignSkeleton from './JuryAssignSkeleton.vue'

const meta: Meta<typeof JuryAssignSkeleton> = {
  title: 'Tournaments/Skeletons/Jury assignment',
  component: JuryAssignSkeleton,
  tags: ['autodocs'],
}

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {}
