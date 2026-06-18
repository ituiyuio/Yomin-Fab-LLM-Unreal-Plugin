<script setup lang="ts">
import { computed } from 'vue'
import { useData, withBase } from 'vitepress'
import { useNews } from '../composables/useNews'

const { list } = useNews()

const { localeIndex } = useData()
const isEn = computed(() => localeIndex.value === 'en')

function cardHref(url: string): string {
  return withBase(url)
}
</script>

<template>
  <div v-if="list.length" class="news-timeline">
    <article
      v-for="(entry, idx) in list"
      :key="entry.slug"
      class="news-timeline-row"
    >
      <div class="news-timeline-rail">
        <span class="news-timeline-dot" />
        <span v-if="idx < list.length - 1" class="news-timeline-line" />
      </div>
      <a :href="cardHref(entry.url)" class="news-timeline-card">
        <div class="news-timeline-meta">
          <span :class="['news-tag', `news-tag-${entry.tag.toLowerCase()}`]">
            {{ entry.tag.toUpperCase() }}
          </span>
          <span class="news-timeline-date">{{ entry.date }}</span>
        </div>
        <h3 class="news-timeline-title">{{ entry.title }}</h3>
        <p class="news-timeline-summary">{{ entry.summary }}</p>
        <span class="news-timeline-cta">{{ isEn ? 'Read more →' : '阅读更多 →' }}</span>
      </a>
    </article>
  </div>
  <p v-else class="news-empty">{{ isEn ? 'No updates yet' : '暂无更新' }}</p>
</template>
