<script setup lang="ts">
import { computed } from 'vue'
import { useData, withBase } from 'vitepress'
import DefaultTheme from 'vitepress/theme'
import NewsEntryHeader from './components/NewsEntryHeader.vue'

const { frontmatter, localeIndex } = useData()
const isEn = computed(() => localeIndex.value === 'en')

const allNewsHref = computed(() => withBase(isEn.value ? '/en/news/' : '/news/'))
const backText = computed(() => (isEn.value ? '← Back to all news' : '← 返回新闻列表'))

// A page is a news entry when its front-matter has both `tag` and `slug` —
// fields that are unique to news entries (regular doc pages don't use them).
</script>

<template>
  <DefaultTheme.Layout>
    <template #doc-before>
      <NewsEntryHeader
        v-if="frontmatter.tag && frontmatter.slug"
        :tag="frontmatter.tag"
        :title="frontmatter.title"
        :date="frontmatter.date"
      />
    </template>
    <template #doc-after>
      <footer
        v-if="frontmatter.tag && frontmatter.slug"
        class="news-entry-footer"
      >
        <a :href="allNewsHref" class="news-back-link">{{ backText }}</a>
      </footer>
    </template>
  </DefaultTheme.Layout>
</template>
