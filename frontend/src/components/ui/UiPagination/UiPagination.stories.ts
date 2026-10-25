import type { Meta, StoryObj } from '@storybook/vue3-vite'
import { ref } from 'vue'
import { fn } from 'storybook/test'
import UiPagination from './UiPagination.vue'

const meta: Meta<typeof UiPagination> = {
  title: 'UI/UiPagination',
  component: UiPagination,
  tags: ['autodocs'],
  argTypes: {
    modelValue: { table: { disable: true } },
    totalItems: { control: 'number', min: 1 },
    pageSize: { control: 'number', min: 1 },
    maxVisible: { control: 'number', min: 3 },
    showSummary: { control: 'boolean' },
  },
  args: {
    'onUpdate:modelValue': fn(),
    totalItems: 100,
    pageSize: 10,
    maxVisible: 5,
    showSummary: true,
  },
}

export default meta
type Story = StoryObj<typeof meta>

/** Default pagination (100 items, 10 per page = 10 pages). */
export const Default: Story = {
  render: (args) => ({
    components: { UiPagination },
    setup() {
      const page = ref(1)
      return { args, page }
    },
    template: `
      <div>
        <ui-pagination v-bind="args" v-model="page" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Current page: {{ page }}
        </p>
      </div>
    `,
  }),
}

/** Pagination on first page. */
export const FirstPage: Story = {
  render: (args) => ({
    components: { UiPagination },
    setup() {
      const page = ref(1)
      return { args, page }
    },
    template: `
      <div>
        <ui-pagination v-bind="args" v-model="page" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Current page: {{ page }}
        </p>
      </div>
    `,
  }),
}

/** Pagination on middle page. */
export const MiddlePage: Story = {
  render: (args) => ({
    components: { UiPagination },
    setup() {
      const page = ref(5)
      return { args, page }
    },
    template: `
      <div>
        <ui-pagination v-bind="args" v-model="page" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Current page: {{ page }}
        </p>
      </div>
    `,
  }),
}

/** Pagination on last page. */
export const LastPage: Story = {
  render: (args) => ({
    components: { UiPagination },
    setup() {
      const page = ref(10)
      return { args, page }
    },
    template: `
      <div>
        <ui-pagination v-bind="args" v-model="page" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Current page: {{ page }}
        </p>
      </div>
    `,
  }),
}

/** Pagination with many pages (500 items, 10 per page = 50 pages). */
export const ManyPages: Story = {
  args: { totalItems: 500, maxVisible: 7 },
  render: (args) => ({
    components: { UiPagination },
    setup() {
      const page = ref(1)
      return { args, page }
    },
    template: `
      <div>
        <ui-pagination v-bind="args" v-model="page" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Current page: {{ page }} / {{ Math.ceil(args.totalItems / args.pageSize) }}
        </p>
      </div>
    `,
  }),
}

/** Pagination on middle page with many total pages. */
export const ManyPagesMiddle: Story = {
  args: { totalItems: 500, maxVisible: 7 },
  render: (args) => ({
    components: { UiPagination },
    setup() {
      const page = ref(25)
      return { args, page }
    },
    template: `
      <div>
        <ui-pagination v-bind="args" v-model="page" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Current page: {{ page }} / {{ Math.ceil(args.totalItems / args.pageSize) }}
        </p>
      </div>
    `,
  }),
}

/** Pagination near end with many total pages. */
export const ManyPagesEnd: Story = {
  args: { totalItems: 500, maxVisible: 7 },
  render: (args) => ({
    components: { UiPagination },
    setup() {
      const page = ref(48)
      return { args, page }
    },
    template: `
      <div>
        <ui-pagination v-bind="args" v-model="page" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Current page: {{ page }} / {{ Math.ceil(args.totalItems / args.pageSize) }}
        </p>
      </div>
    `,
  }),
}

/** Pagination with custom page size (25 per page). */
export const CustomPageSize: Story = {
  args: { pageSize: 25 },
  render: (args) => ({
    components: { UiPagination },
    setup() {
      const page = ref(2)
      return { args, page }
    },
    template: `
      <div>
        <ui-pagination v-bind="args" v-model="page" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Current page: {{ page }}
        </p>
      </div>
    `,
  }),
}

/** Pagination without summary. */
export const NoSummary: Story = {
  args: { showSummary: false },
  render: (args) => ({
    components: { UiPagination },
    setup() {
      const page = ref(3)
      return { args, page }
    },
    template: `
      <div>
        <ui-pagination v-bind="args" v-model="page" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Current page: {{ page }} (no summary)
        </p>
      </div>
    `,
  }),
}

/** Small total items (less than one page). */
export const SinglePage: Story = {
  args: { totalItems: 5 },
  render: (args) => ({
    components: { UiPagination },
    setup() {
      const page = ref(1)
      return { args, page }
    },
    template: `
      <div>
        <ui-pagination v-bind="args" v-model="page" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Current page: {{ page }} (only 5 items)
        </p>
      </div>
    `,
  }),
}

/** Controlled pagination with v-model. */
export const Controlled: Story = {
  render: () => ({
    components: { UiPagination },
    setup() {
      const page = ref(3)
      return { page }
    },
    template: `
      <div>
        <ui-pagination v-model="page" :total-items="200" :page-size="20" />
        <p class="text-muted" style="margin-top: 0.5rem; font-size: 0.8rem;">
          Current page: {{ page }}
        </p>
      </div>
    `,
  }),
}
