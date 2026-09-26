import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface SettingsState {
  language: string;
  timezone: string;
  dateFormat: string;
  itemsPerPage: number;
  autoSave: boolean;
  emailNotifications: boolean;
  pushNotifications: boolean;
}

const initialState: SettingsState = {
  language: 'tr',
  timezone: 'Europe/Istanbul',
  dateFormat: 'DD.MM.YYYY',
  itemsPerPage: 20,
  autoSave: true,
  emailNotifications: true,
  pushNotifications: false,
};

export const settingsSlice = createSlice({
  name: 'settings',
  initialState,
  reducers: {
    updateSettings: (state, action: PayloadAction<Partial<SettingsState>>) => {
      Object.assign(state, action.payload);
    },
    resetSettings: () => initialState,
  },
});

export const { updateSettings, resetSettings } = settingsSlice.actions;
export default settingsSlice.reducer;
