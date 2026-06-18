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
  </DefaultTheme.Layout>
</template>
