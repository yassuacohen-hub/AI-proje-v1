import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface Identifiable {
  id: string;
}

export interface DataState<T> {
  items: T[];
  selectedId: string | null;
  loading: boolean;
  error: string | null;
  lastUpdated: number | null;
}

function createDataSlice<T extends Identifiable>(name: string) {
  const initialState: DataState<T> = {
    items: [],
    selectedId: null,
    loading: false,
    error: null,
    lastUpdated: null,
  };

  const slice = createSlice({
    name,
    initialState,
    reducers: {
      fetchStart: (state) => {
        state.loading = true;
        state.error = null;
      },
      fetchSuccess: (state, action: PayloadAction<T[]>) => {
        state.loading = false;
        state.items = action.payload as typeof state.items;
        state.lastUpdated = Date.now();
      },
      fetchFailure: (state, action: PayloadAction<string>) => {
        state.loading = false;
        state.error = action.payload;
      },
      addItem: (state, action: PayloadAction<T>) => {
        state.items.push(action.payload as (typeof state.items)[number]);
      },
      updateItem: (state, action: PayloadAction<T>) => {
        const index = state.items.findIndex((item) => item.id === action.payload.id);
        if (index !== -1) state.items[index] = action.payload as (typeof state.items)[number];
      },
      removeItem: (state, action: PayloadAction<string>) => {
        state.items = state.items.filter((item) => item.id !== action.payload);
      },
      setSelected: (state, action: PayloadAction<string | null>) => {
        state.selectedId = action.payload;
      },
    },
  });

  return slice;
}

export const usersSlice = createDataSlice<Identifiable & { name: string; email: string }>('users');
export const projectsSlice = createDataSlice<Identifiable & { name: string; status: string }>('projects');
export const analyticsSlice = createDataSlice<Identifiable & { metric: string; value: number }>('analytics');

export const {
  fetchStart: fetchUsersStart,
  fetchSuccess: fetchUsersSuccess,
  fetchFailure: fetchUsersFailure,
  addItem: addUser,
  updateItem: updateUser,
  removeItem: removeUser,
  setSelected: setSelectedUser,
} = usersSlice.actions;

export const {
  fetchStart: fetchProjectsStart,
  fetchSuccess: fetchProjectsSuccess,
  fetchFailure: fetchProjectsFailure,
  addItem: addProject,
  updateItem: updateProject,
  removeItem: removeProject,
  setSelected: setSelectedProject,
} = projectsSlice.actions;

export const {
  fetchStart: fetchAnalyticsStart,
  fetchSuccess: fetchAnalyticsSuccess,
  fetchFailure: fetchAnalyticsFailure,
  addItem: addAnalytics,
  updateItem: updateAnalytics,
  removeItem: removeAnalytics,
  setSelected: setSelectedAnalytics,
} = analyticsSlice.actions;

export default {
  users: usersSlice.reducer,
  projects: projectsSlice.reducer,
  analytics: analyticsSlice.reducer,
};
