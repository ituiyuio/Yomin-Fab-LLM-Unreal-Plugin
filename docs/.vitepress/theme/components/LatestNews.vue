<script setup lang="ts">
import { computed } from 'vue'
import { useData, withBase } from 'vitepress'
import { useNews } from '../composables/useNews'

const props = withDefaults(
  defineProps<{ count?: number }>(),
  { count: 3 }
)

const { list } = useNews()
const items = list.slice(0, props.count)

const { localeIndex } = useData()
const isEn = computed(() => localeIndex.value === 'en')

// withBase prepends the site `base` (e.g. "/Yomin-Fab-LLM-Unreal-Plugin/")
// so the link works when the site is hosted under a sub-path. Raw <a> tags
// don't get this for free — only VPLink does.
const viewAllHref = computed(() => withBase(isEn.value ? '/en/news/' : '/news/'))
const viewAllText = computed(() => (isEn.value ? 'View all →' : '查看全部 →'))

function cardHref(url: string): string {
  return withBase(url)
}
</script>

<template>
  <section v-if="items.length" class="news-section">
    <div class="news-section-head">
      <h2 class="news-section-title">{{ isEn ? 'Latest News' : '最新动态' }}</h2>
      <a :href="viewAllHref" class="news-section-link">{{ viewAllText }}</a>
    </div>

    <div class="news-grid">
      <a
        v-for="(entry, idx) in items"
        :key="entry.slug"
        :href="cardHref(entry.url)"
        class="news-card"
      >
        <div class="news-card-meta">
          <span v-if="entry.emoji" class="news-card-icon">{{ entry.emoji }}</span>
          <span :class="['news-tag', `news-tag-${entry.tag.toLowerCase()}`]">
            {{ entry.tag.toUpperCase() }}
          </span>
          <span class="news-card-date">{{ entry.date }}</span>
          <span v-if="idx === 0" class="news-card-new">{{ isEn ? 'NEW' : '新' }}</span>
        </div>
        <h3 class="news-card-title">{{ entry.title }}</h3>
        <p class="news-card-summary">{{ entry.summary }}</p>
        <span class="news-card-cta">{{ isEn ? 'Read more →' : '阅读更多 →' }}</span>
      </a>
    </div>
  </section>
</template>
