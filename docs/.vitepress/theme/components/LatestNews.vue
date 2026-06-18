<script setup lang="ts">
import { useNews } from '../composables/useNews'

const props = withDefaults(
  defineProps<{ count?: number }>(),
  { count: 3 }
)

const { list } = useNews()
const featured = list[0] ?? null
const rest = list.slice(1, props.count)

function hrefFor(slug: string): string {
  return `/news/${slug}/`
}
</script>

<template>
  <section v-if="featured" class="news-section">
    <h2 class="news-section-title">Latest News</h2>

    <!-- Featured banner: the most recent entry -->
    <a :href="hrefFor(featured.slug)" class="news-banner">
      <span v-if="featured.emoji" class="news-banner-emoji">{{ featured.emoji }}</span>
      <div class="news-banner-meta">
        <span class="news-banner-badge">LATEST</span>
        <span class="news-banner-date">{{ featured.date }}</span>
      </div>
      <h3 class="news-banner-title">{{ featured.title }}</h3>
      <p class="news-banner-summary">{{ featured.summary }}</p>
      <span class="news-banner-cta">Read more →</span>
    </a>

    <!-- Compact cards: entries 2..N -->
    <div v-if="rest.length" class="news-compact-grid">
      <a
        v-for="entry in rest"
        :key="entry.slug"
        :href="hrefFor(entry.slug)"
        class="news-compact-card"
      >
        <span class="news-compact-date">{{ entry.date }}</span>
        <span :class="['news-tag', `news-tag-${entry.tag.toLowerCase()}`]">
          {{ entry.tag.toUpperCase() }}
        </span>
        <span class="news-compact-title">{{ entry.title }}</span>
        <span class="news-compact-arrow">→</span>
      </a>
    </div>
  </section>
</template>
