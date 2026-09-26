import { configureStore } from '@reduxjs/toolkit';
import { authSlice } from './reducers/authSlice';
import { uiSlice } from './reducers/uiSlice';
import dataReducers from './reducers/dataSlice';
import { settingsSlice } from './reducers/settingsSlice';
import { notificationsSlice } from './reducers/notificationsSlice';

const rootReducer = {
  auth: authSlice.reducer,
  ui: uiSlice.reducer,
  users: dataReducers.users,
  projects: dataReducers.projects,
  analytics: dataReducers.analytics,
  settings: settingsSlice.reducer,
  notifications: notificationsSlice.reducer,
};

export const store = configureStore({
  reducer: rootReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
      immutableCheck: false,
    }),
  devTools: process.env.NODE_ENV !== 'production',
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

export default store;
