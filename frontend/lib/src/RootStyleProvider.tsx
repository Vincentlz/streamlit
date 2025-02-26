/**
 * Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022-2025)
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import React, { ReactElement } from "react"

import { BaseProvider } from "baseui"
import createCache from "@emotion/cache"
import {
  CacheProvider,
  ThemeProvider as EmotionThemeProvider,
  Global,
} from "@emotion/react"

import { globalStyles, ThemeConfig } from "./theme"

export interface RootStyleProviderProps {
  theme: ThemeConfig
  children: React.ReactNode
}

const nonce = document.currentScript?.nonce || ""
const cache = createCache({
  // The key field is required but only matters if there's more than one
  // emotion cache in use. This will probably never be true for us, so we just
  // set it arbitrarily.
  key: "st-emotion-cache",
  ...(nonce && { nonce }),
})

export function RootStyleProvider(
  props: RootStyleProviderProps
): ReactElement {
  const { children, theme } = props
  return (
    <BaseProvider
      theme={theme.basewebTheme}
      // This zIndex is required for modals/dialog. However,
      // it would be good to do some investigation
      // and find a better way to configure the zIndex
      // for the modals/dialogs.
      zIndex={theme.emotion.zIndices.popup}
    >
      <CacheProvider value={cache}>
        <EmotionThemeProvider theme={theme.emotion}>
          <Global styles={globalStyles} />
          {children}
        </EmotionThemeProvider>
      </CacheProvider>
    </BaseProvider>
  )
}
