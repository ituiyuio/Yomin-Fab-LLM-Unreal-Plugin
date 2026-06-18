import DefaultTheme from 'vitepress/theme'
import Layout from './Layout.vue'
import LatestNews from './components/LatestNews.vue'
import NewsList from './components/NewsList.vue'
import './style.css'

export default {
  extends: DefaultTheme,
  Layout, // override the default theme's Layout
  enhanceApp({ app }) {
    app.component('LatestNews', LatestNews)
    app.component('NewsList', NewsList)
  }
}
