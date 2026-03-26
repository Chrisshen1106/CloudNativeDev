import { ref } from 'vue'
import zhTW from '@/locales/zh-TW.js'
import en from '@/locales/en.js'

const locales = { 'zh-TW': zhTW, en }
const currentLocale = ref(localStorage.getItem('ams_locale') || 'zh-TW')

export function useI18n() {
  function t(key) {
    const segments = key.split('.')
    let value = locales[currentLocale.value]
    for (const seg of segments) {
      value = value?.[seg]
    }
    return value ?? key
  }

  function setLocale(locale) {
    if (locales[locale]) {
      currentLocale.value = locale
      localStorage.setItem('ams_locale', locale)
    }
  }

  return { t, currentLocale, setLocale }
}
