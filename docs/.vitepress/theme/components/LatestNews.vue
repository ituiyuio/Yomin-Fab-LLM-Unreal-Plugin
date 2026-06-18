<script setup lang="ts">
import { useNews } from '../composables/useNews'

const props = withDefaults(
  defineProps<{ count?: number }>(),
  { count: 3 }
)

const { list } = useNews()
const items = list.slice(0, props.count)

function hrefFor(slug: string): string {
  return `/news/${slug}/`
}
</script>

<template>
  <section v-if="items.length" class="news-section">
    <div class="news-section-head">
      <h2 class="news-section-title">Latest News</h2>
      <a href="/news/" class="news-section-link">View all →</a>
    </div>

    <div class="news-grid">
      <a
        v-for="(entry, idx) in items"
        :key="entry.slug"
        :href="hrefFor(entry.slug)"
        class="news-card"
      >
        <div class="news-card-meta">
          <span v-if="entry.emoji" class="news-card-icon">{{ entry.emoji }}</span>
          <span :class="['news-tag', `news-tag-${entry.tag.toLowerCase()}`]">
            {{ entry.tag.toUpperCase() }}
          </span>
          <span class="news-card-date">{{ entry.date }}</span>
          <span v-if="idx === 0" class="news-card-new">NEW</span>
        </div>
        <h3 class="news-card-title">{{ entry.title }}</h3>
        <p class="news-card-summary">{{ entry.summary }}</p>
        <span class="news-card-cta">Read more →</span>
      </a>
    </div>
  </section>
</template>
