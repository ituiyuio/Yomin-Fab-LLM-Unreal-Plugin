import DefaultTheme from 'vitepress/theme'
import LatestNews from './components/LatestNews.vue'
import NewsList from './components/NewsList.vue'
import './style.css'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('LatestNews', LatestNews)
    app.component('NewsList', NewsList)
  }
}
