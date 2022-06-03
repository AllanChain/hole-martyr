import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import Unocss from 'unocss/vite'
import { presetIcons, presetUno } from 'unocss'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    Unocss({
      presets: [
        presetUno(),
        presetIcons(),
      ],
      shortcuts: {
        btn: 'border-none py-1 px-2 rounded m-1',
      },
    }),
  ],
})
