export function reducer(state, action) {
  const draft = { ...state };
  switch (action.type) {
    case "UPDATE_USERNAME":
      draft.username = action.payload;
      break;
  }
  return draft;
}
