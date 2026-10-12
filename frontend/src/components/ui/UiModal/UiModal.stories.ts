import type { Meta, StoryObj } from '@storybook/vue3-vite'
import { ref } from 'vue'
import { fn } from 'storybook/test'
import UiModal from '@/components/ui/UiModal'
import UiButton from '@/components/ui/UiButton'

const meta: Meta<typeof UiModal> = {
  title: 'UI/UiModal',
  component: UiModal,
  tags: ['autodocs'],
  argTypes: {
    maxWidth: { control: 'text' },
    closeOnBackdrop: { control: 'boolean' },
    scrollable: { control: 'boolean' },
  },
  args: {
    'onUpdate:modelValue': fn(),
    maxWidth: '520px',
    closeOnBackdrop: true,
    scrollable: false,
  },
}

export default meta
type Story = StoryObj<typeof meta>

/** Basic modal - closed by default, click button to open. */
export const Closed: Story = {
  render: (args) => ({
    components: { UiModal, UiButton },
    setup() {
      const isOpen = ref(false)
      const onClose = fn()
      return { args, isOpen, onClose }
    },
    template: `
      <div>
        <ui-button @click="isOpen = true">Open Modal</ui-button>
        <ui-modal v-bind="args" v-model="isOpen" @close="onClose">
          <template #title>Modal Title</template>
          <p>This is the modal content. Click the button above to open/close.</p>
        </ui-modal>
      </div>
    `,
  }),
}

/** Modal with custom maxWidth. */
export const Large: Story = {
  args: { maxWidth: '720px' },
  render: (args) => ({
    components: { UiModal, UiButton },
    setup() {
      const isOpen = ref(false)
      const onClose = fn()
      return { args, isOpen, onClose }
    },
    template: `
      <div>
        <ui-button @click="isOpen = true">Open Large Modal (720px)</ui-button>
        <ui-modal v-bind="args" v-model="isOpen" @close="onClose">
          <template #title>Large Modal (720px)</template>
          <p>This modal uses a custom <code>maxWidth</code> of 720px.</p>
          <p class="text-muted">Useful for forms or complex content that needs more space.</p>
        </ui-modal>
      </div>
    `,
  }),
}

/** Modal with scrollable content. */
export const Scrollable: Story = {
  args: { scrollable: true },
  render: (args) => ({
    components: { UiModal, UiButton },
    setup() {
      const isOpen = ref(false)
      const onClose = fn()
      return { args, isOpen, onClose }
    },
    template: `
      <div>
        <ui-button @click="isOpen = true">Open Scrollable Modal</ui-button>
        <ui-modal v-bind="args" v-model="isOpen" style="max-height: 400px" @close="onClose">
          <template #title>Scrollable Modal</template>
          <div v-for="i in 20" :key="i" style="padding: 1rem 0; border-bottom: 1px solid var(--border);">
            <p>Content row {{ i }} - Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>
          </div>
        </ui-modal>
      </div>
    `,
  }),
}

/** Modal with closeOnBackdrop disabled. */
export const NoBackdropClose: Story = {
  args: { closeOnBackdrop: false },
  render: (args) => ({
    components: { UiModal, UiButton },
    setup() {
      const isOpen = ref(false)
      const onClose = fn()
      return { args, isOpen, onClose }
    },
    template: `
      <div>
        <ui-button @click="isOpen = true">Open Modal (No Backdrop Close)</ui-button>
        <ui-modal v-bind="args" v-model="isOpen" @close="onClose">
          <template #title>No Backdrop Close</template>
          <p>This modal cannot be closed by clicking the backdrop.</p>
          <p class="text-muted">Use the close button or press Escape to close.</p>
        </ui-modal>
      </div>
    `,
  }),
}

/** Controlled modal with v-model. */
export const Controlled: Story = {
  render: () => ({
    components: { UiModal, UiButton },
    setup() {
      const isOpen = ref(false)
      const onClose = fn()
      return { isOpen, onClose }
    },
    template: `
      <div>
        <ui-button @click="isOpen = true">Open Controlled Modal</ui-button>
        <ui-modal v-model="isOpen" max-width="400px" @close="onClose">
          <template #title>Controlled Modal</template>
          <p>This modal is controlled via v-model.</p>
        </ui-modal>
      </div>
    `,
  }),
}

/** Modal with custom footer. */
export const WithFooter: Story = {
  render: (args) => ({
    components: { UiModal, UiButton },
    setup() {
      const isOpen = ref(false)
      const onClose = fn()
      const onSave = fn()
      return { args, isOpen, onClose, onSave }
    },
    template: `
      <div>
        <ui-button @click="isOpen = true">Open Modal with Footer</ui-button>
        <ui-modal v-bind="args" v-model="isOpen" @close="onClose">
          <template #title>Modal with Footer</template>
          <p>This modal has custom footer actions.</p>
          <template #footer>
            <ui-button size="sm" variant="secondary" @click="onClose">Cancel</ui-button>
            <ui-button size="sm" @click="onSave">Save</ui-button>
          </template>
        </ui-modal>
      </div>
    `,
  }),
}

/** Small modal. */
export const Small: Story = {
  args: { maxWidth: '320px' },
  render: (args) => ({
    components: { UiModal, UiButton },
    setup() {
      const isOpen = ref(false)
      const onClose = fn()
      return { args, isOpen, onClose }
    },
    template: `
      <div>
        <ui-button @click="isOpen = true">Open Small Modal (320px)</ui-button>
        <ui-modal v-bind="args" v-model="isOpen" @close="onClose">
          <template #title>Small Modal</template>
          <p>Compact modal with 320px max width.</p>
        </ui-modal>
      </div>
    `,
  }),
}

/** Modal with long content and scroll. */
export const LongContent: Story = {
  args: { scrollable: true },
  render: (args) => ({
    components: { UiModal, UiButton },
    setup() {
      const isOpen = ref(false)
      const onClose = fn()
      return { args, isOpen, onClose }
    },
    template: `
      <div>
        <ui-button @click="isOpen = true">Open Long Content Modal</ui-button>
        <ui-modal v-bind="args" v-model="isOpen" style="max-height: 500px" @close="onClose">
          <template #title>Long Content with Scroll</template>
          <div style="padding: 1rem 0;">
            <p style="margin-bottom: 1rem;"><strong>Lorem ipsum dolor sit amet,</strong> consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
            <p style="margin-bottom: 1rem;">Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.</p>
            <p style="margin-bottom: 1rem;">Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>
            <p style="margin-bottom: 1rem;">Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo.</p>
            <p style="margin-bottom: 1rem;">Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt.</p>
            <p style="margin-bottom: 1rem;">Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem.</p>
          </div>
        </ui-modal>
      </div>
    `,
  }),
}
