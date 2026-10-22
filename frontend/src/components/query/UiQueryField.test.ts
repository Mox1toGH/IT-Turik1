import { describe, expect, it } from 'vitest'
import { render } from 'vitest-browser-vue'
import { computed, defineComponent, h, provide, ref } from 'vue'
import UiQueryField from './UiQueryField.vue'
import { queryContextKey } from './queryContext'

function fieldHost(options: { loading?: boolean; fetching?: boolean; skeleton?: boolean } = {}) {
  return defineComponent({
    setup() {
      provide(queryContextKey, {
        isInitialLoading: computed(() => options.loading ?? false),
        isFetching: computed(() => options.fetching ?? false),
      })
      return () =>
        h(UiQueryField, options.loading === undefined ? {} : { loading: options.loading }, {
          ...(options.skeleton === false
            ? {}
            : { skeleton: () => h('i', { 'data-testid': 'skeleton' }, 'Loading') }),
          default: () => h('span', { 'data-testid': 'content' }, 'Content'),
        })
    },
  })
}

describe('UiQueryField', () => {
  it('shows the skeleton for explicit loading', () => {
    const screen = render(fieldHost({ loading: true }))
    expect(screen.getByTestId('skeleton')).toBeInTheDocument()
    expect(screen.getByTestId('content').query()).toBeNull()
  })

  it('explicit loading false overrides inherited loading', () => {
    const screen = render(fieldHost({ loading: false }))
    expect(screen.getByTestId('content')).toBeInTheDocument()
    expect(screen.getByTestId('skeleton').query()).toBeNull()
  })

  it('uses inherited initial loading when no override is passed', () => {
    const Wrapper = defineComponent({
      setup: () => () =>
        h(
          UiQueryField,
          {},
          {
            skeleton: () => h('i', { 'data-testid': 'skeleton' }, 'Loading'),
            default: () => h('span', { 'data-testid': 'content' }, 'Content'),
          },
        ),
    })
    const Parent = defineComponent({
      setup() {
        provide(queryContextKey, {
          isInitialLoading: computed(() => true),
          isFetching: computed(() => false),
        })
        return () => h(Wrapper)
      },
    })
    const screen = render(Parent)
    expect(screen.getByTestId('skeleton')).toBeInTheDocument()
    expect(screen.getByTestId('content').query()).toBeNull()
  })

  it('works outside a block with explicit loading and leaves content visible without a skeleton', () => {
    const screen = render(UiQueryField, {
      props: { loading: true },
      slots: {
        skeleton: '<span>Standalone skeleton</span>',
        default: '<span>Standalone content</span>',
      },
    })
    expect(screen.getByText('Standalone skeleton')).toBeInTheDocument()
    expect(screen.getByText('Standalone content').query()).toBeNull()

    const noSkeleton = render(UiQueryField, {
      props: { loading: true },
      slots: { default: '<span>Standalone content without skeleton</span>' },
    })
    expect(noSkeleton.getByText('Standalone content without skeleton')).toBeInTheDocument()
  })

  it('dims existing content while fetching without replacing it with a skeleton', async () => {
    const fetching = ref(false)
    const Wrapper = defineComponent({
      setup() {
        provide(queryContextKey, {
          isInitialLoading: computed(() => false),
          isFetching: computed(() => fetching.value),
        })
        return () =>
          h(
            UiQueryField,
            {},
            {
              skeleton: () => h('i', { 'data-testid': 'skeleton' }, 'Loading'),
              default: () => h('span', { 'data-testid': 'content' }, 'Content'),
            },
          )
      },
    })
    const screen = render(Wrapper)
    fetching.value = true
    await expect
      .poll(() => screen.getByTestId('content').element().parentElement?.className)
      .toContain('is-background-fetching')
    expect(screen.getByTestId('content')).toBeInTheDocument()
    expect(screen.getByTestId('skeleton').query()).toBeNull()
    expect(getComputedStyle(screen.getByTestId('content').element()).opacity).toBe('0.6')

    fetching.value = false
    await expect
      .poll(() => getComputedStyle(screen.getByTestId('content').element()).opacity)
      .toBe('1')
  })

  it('does not dim the skeleton while initial loading', () => {
    const screen = render(fieldHost({ loading: true, fetching: true }))
    expect(screen.getByTestId('skeleton')).toBeInTheDocument()
    expect(getComputedStyle(screen.getByTestId('skeleton').element()).opacity).toBe('1')
  })
})
