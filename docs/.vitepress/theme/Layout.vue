<script setup lang="ts">
import { useData } from 'vitepress'
import DefaultTheme from 'vitepress/theme'
import NewsEntryHeader from './components/NewsEntryHeader.vue'

const { frontmatter } = useData()

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
        <a href="/news/" class="news-back-link">← Back to all news</a>
      </footer>
    </template>
  </DefaultTheme.Layout>
</template>
