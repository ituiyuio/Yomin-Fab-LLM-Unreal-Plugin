<script setup lang="ts">
interface Props {
  tag: string
  title: string
  date: string
}
defineProps<Props>()
</script>

<template>
  <header class="news-entry-header">
    <span :class="['news-tag', `news-tag-${tag.toLowerCase()}`]">
      {{ tag.toUpperCase() }}
    </span>
    <h1 class="news-entry-title">{{ title }}</h1>
    <span class="news-entry-date">{{ date }}</span>
  </header>
</template>
