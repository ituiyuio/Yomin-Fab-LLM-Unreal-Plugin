<script setup lang="ts">
import { useData } from 'vitepress'
import DefaultTheme from 'vitepress/theme'
import NewsEntryHeader from '../components/NewsEntryHeader.vue'

const { frontmatter } = useData()
</script>

<template>
  <DefaultTheme.Layout>
    <template #doc-before>
      <NewsEntryHeader
        :tag="frontmatter.tag"
        :title="frontmatter.title"
        :date="frontmatter.date"
      />
    </template>
    <template #doc-after>
      <footer class="news-entry-footer">
        <a href="/news/" class="news-back-link">← Back to all news</a>
      </footer>
    </template>
  </DefaultTheme.Layout>
</template>
