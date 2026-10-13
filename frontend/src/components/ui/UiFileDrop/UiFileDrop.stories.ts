import type { Meta, StoryObj } from '@storybook/vue3-vite'
import { ref } from 'vue'
import { fn } from 'storybook/test'
import UiFileDrop from './UiFileDrop.vue'

const meta: Meta<typeof UiFileDrop> = {
  title: 'UI/UiFileDrop',
  component: UiFileDrop,
  tags: ['autodocs'],
  argTypes: {
    modelValue: { table: { disable: true } },
    accept: { control: 'text' },
    multiple: { control: 'boolean' },
    disabled: { control: 'boolean' },
    maxFiles: { control: 'number', min: 1 },
    maxSizeMb: { control: 'number', min: 1 },
    hint: { control: 'text' },
  },
  args: {
    'onUpdate:modelValue': fn(),
    accept: undefined,
    multiple: true,
    disabled: false,
    maxFiles: undefined,
    maxSizeMb: undefined,
    hint: undefined,
  },
}

export default meta
type Story = StoryObj<typeof meta>

/** Default file drop zone. */
export const Default: Story = {
  render: (args) => ({
    components: { UiFileDrop },
    setup() {
      const files = ref<File[]>([])
      return { args, files }
    },
    template: `
      <div style="max-width: 480px;">
        <ui-file-drop v-bind="args" v-model="files" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Files: {{ files.length }}
        </p>
      </div>
    `,
  }),
}

/** Single file upload (multiple=false). */
export const SingleFile: Story = {
  args: { multiple: false },
  render: (args) => ({
    components: { UiFileDrop },
    setup() {
      const files = ref<File[]>([])
      return { args, files }
    },
    template: `
      <div style="max-width: 480px;">
        <ui-file-drop v-bind="args" v-model="files" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          File: {{ files[0]?.name || 'none' }}
        </p>
      </div>
    `,
  }),
}

/** Disabled state. */
export const Disabled: Story = {
  args: { disabled: true },
  render: (args) => ({
    components: { UiFileDrop },
    setup() {
      const files = ref<File[]>([])
      return { args, files }
    },
    template: `
      <div style="max-width: 480px;">
        <ui-file-drop v-bind="args" v-model="files" />
      </div>
    `,
  }),
}

/** Image-only accept. */
export const ImagesOnly: Story = {
  args: { accept: 'image/*' },
  render: (args) => ({
    components: { UiFileDrop },
    setup() {
      const files = ref<File[]>([])
      return { args, files }
    },
    template: `
      <div style="max-width: 480px;">
        <ui-file-drop v-bind="args" v-model="files" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Files: {{ files.length }}
        </p>
      </div>
    `,
  }),
}

/** PDF only accept. */
export const PDFOnly: Story = {
  args: { accept: '.pdf,application/pdf' },
  render: (args) => ({
    components: { UiFileDrop },
    setup() {
      const files = ref<File[]>([])
      return { args, files }
    },
    template: `
      <div style="max-width: 480px;">
        <ui-file-drop v-bind="args" v-model="files" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Files: {{ files.length }}
        </p>
      </div>
    `,
  }),
}

/** With max files limit. */
export const MaxFiles: Story = {
  args: { maxFiles: 3 },
  render: (args) => ({
    components: { UiFileDrop },
    setup() {
      const files = ref<File[]>([])
      return { args, files }
    },
    template: `
      <div style="max-width: 480px;">
        <ui-file-drop v-bind="args" v-model="files" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Files: {{ files.length }} / {{ args.maxFiles }}
        </p>
      </div>
    `,
  }),
}

/** With max size limit. */
export const MaxSize: Story = {
  args: { maxSizeMb: 2 },
  render: (args) => ({
    components: { UiFileDrop },
    setup() {
      const files = ref<File[]>([])
      return { args, files }
    },
    template: `
      <div style="max-width: 480px;">
        <ui-file-drop v-bind="args" v-model="files" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Files: {{ files.length }}
        </p>
      </div>
    `,
  }),
}

/** With custom hint. */
export const CustomHint: Story = {
  args: { hint: 'Upload your avatar (PNG, JPG up to 5MB)' },
  render: (args) => ({
    components: { UiFileDrop },
    setup() {
      const files = ref<File[]>([])
      return { args, files }
    },
    template: `
      <div style="max-width: 480px;">
        <ui-file-drop v-bind="args" v-model="files" />
      </div>
    `,
  }),
}
