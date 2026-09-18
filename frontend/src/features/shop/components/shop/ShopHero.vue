<template>
  <header class="shop-hero">
    <div class="shop-hero-copy">
      <div class="breadcrumb-label">
        <span>Shop</span>
        <span aria-hidden="true">/</span>
        <span>Catalog</span>
      </div>

      <h1 class="text-6xl">Catalog</h1>
      <p class="section-subtitle text-xl">
        Browse available products and redeem them with your points.
      </p>
    </div>

    <div class="hero-actions">
      <ui-skeleton-loader :loading="isLoading">
        <template #skeleton>
          <ui-skeleton variant="rect" width="148px" height="45px" />
        </template>

        <ui-card variant="stat" class="shop-stat-card">
          <span class="text-sm">Total products:</span>
          <strong class="text-xl">{{ totalProducts }}</strong>
        </ui-card>
      </ui-skeleton-loader>

      <template v-if="isAdmin">
        <ui-button variant="secondary" size="lg" @click="emit('manage-categories')">
          Manage Categories
        </ui-button>
        <ui-button size="lg" @click="emit('create-product')">
          <span class="create-plus text-2xl" aria-hidden="true">+</span>
          Create Product
        </ui-button>
        <ui-button variant="secondary" as-link to="/admin/shop-orders" size="lg">
          Admin Orders
        </ui-button>
      </template>
    </div>
  </header>
</template>

<script setup lang="ts">
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiSkeletonLoader from '@/components/ui/UiSkeletonLoader.vue'

withDefaults(
  defineProps<{
    totalProducts?: number
    isLoading?: boolean
    isAdmin?: boolean
  }>(),
  { totalProducts: 0, isLoading: false, isAdmin: false },
)

const emit = defineEmits<{
  'create-product': []
  'manage-categories': []
}>()
</script>

<style scoped>
.shop-hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1.5rem;
}

.shop-hero-copy {
  min-width: 0;
}

.breadcrumb-label {
  display: inline-flex;
  align-items: center;
  gap: 0.7rem;
  margin-bottom: 0.75rem;
  color: var(--accent-strong);
  font-size: var(--text-sm);
  line-height: var(--text-sm--line-height);
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.shop-hero h1 {
  margin: 0;
  max-width: 760px;
  color: var(--foreground);
  font-size: var(--text-4xl);
  line-height: var(--text-4xl--line-height);
  font-family: var(--font-display);
  font-weight: 800;
}

.shop-hero .section-subtitle {
  margin: 0.45rem 0 0;
  max-width: 780px;
  font-size: var(--text-base);
  line-height: var(--text-base--line-height);
}

.hero-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: flex-end;
  align-items: center;
}

.shop-stat-card strong {
  font-weight: 800;
}

.shop-stat-card span {
  color: var(--muted-foreground);
  font-weight: 700;
  white-space: nowrap;
}

.create-plus {
  font-weight: 800;
  line-height: 1;
}

@media (max-width: 760px) {
  .shop-hero {
    align-items: stretch;
    flex-direction: column;
    gap: 1rem;
  }

  .shop-hero h1 {
    font-size: var(--text-3xl);
    line-height: var(--text-3xl--line-height);
  }

  .shop-hero .section-subtitle {
    font-size: var(--text-sm);
    line-height: var(--text-sm--line-height);
  }

  .hero-actions {
    justify-content: flex-start;
  }
}
</style>
